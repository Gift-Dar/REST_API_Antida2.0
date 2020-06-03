import datetime
import sqlite3

from exceptions import ServiceError


class AdsServiceError(ServiceError):
    service = 'ads'


class AdDoesNotExistError(AdsServiceError):
    pass


class AdsService:
    def __init__(self, connection):
        self.connection = connection

    def phorm_dict_ad(self, ad_id):
        cur = self.connection.cursor()
        cur.execute(f"""
            SELECT account.id
            FROM account
                JOIN seller ON account.id=seller.account_id
                JOIN ad ON seller.id=ad.seller_id
            WHERE ad.id = {ad_id}
        """)
        result = cur.fetchone()
        if result is None:
            raise AdDoesNotExistError(ad_id)
        account_id = result[0]
        cur.execute(f"""
            SELECT seller.id
            FROM seller
                JOIN ad ON seller.id=ad.seller_id
            WHERE ad.id = {ad_id}
        """)
        result = cur.fetchone()
        seller_id = result[0]
        cur.execute(f"""
            SELECT title, date
            FROM ad
            WHERE ad.id = {ad_id}
        """)
        result = cur.fetchone()
        title = result[0]
        date = result[1]
        cur.execute(f"""
            SELECT name
            FROM tag
                JOIN adtag ON tag.id=adtag.tag_id
            WHERE adtag.ad_id = {ad_id}
        """)
        result = cur.fetchall()
        tags = []
        for tag in result:
            tags.append(tag[0])
    
        cur.execute(f"""
            SELECT make, model, mileage, num_owners, reg_number
            FROM car
                JOIN ad ON car.id=ad.car_id
            WHERE ad.id = {ad_id}
        """)
        car = cur.fetchone()
        query = (f"""
            SELECT
                color.*
            FROM color
                JOIN carcolor ON carcolor.color_id=color.id
                JOIN car ON carcolor.car_id=car.id
            WHERE car.id = (
                SELECT car.id
                FROM car
                    JOIN ad ON car.id=ad.car_id
                WHERE ad.id = {ad_id}
                )
            """)
        cur.execute(query)
        dict_color = cur.fetchall()
        color = [dict(color) for color in dict_color]
    
        query = (f"""
            SELECT image.title, image.url
            FROM image
                JOIN car ON image.car_id=car.id
            WHERE car.id = (
                SELECT car.id
                FROM car
                    JOIN ad ON car.id=ad.car_id
                WHERE ad.id = {ad_id}
                )
        """)
        cur.execute(query)
        dict_image = cur.fetchall()
        image = [dict(image) for image in dict_image]
        return {
            'id': f'{account_id}',
            'seller_id': f'{seller_id}',
            'title': f'{title}',
            'date': f'{date}',
            'tags': f'{tags}',
            'car': dict(make=f'{car[0]}', model=f'{car[1]}', colors=f'{color}', mileage=f'{car[2]}',
                        num_owners=f'{car[3]}', reg_number=f'{car[4]}', images=f'{image}')
        }
    
    def build_ads_query(self, filters):
        query_template = """
            SELECT DISTINCT ad.id
            FROM ad
                JOIN seller ON ad.seller_id=seller.id
                JOIN car ON ad.car_id=car.id
                JOIN adtag ON ad.id=adtag.ad_id
                JOIN tag ON adtag.tag_id=tag.id
            {where_query}
        """
        where_clauses = []
        params = []
        for key, value in filters.items():
            if key == 'tags':
                tags = value.split(',')
                tag_query = []
                for tag in tags:
                    tag_query.append(f' tag.name = ?')
                    params.append(tag.lower())
                result_query = ' {}'.format(' OR '.join(tag_query))
                where_clauses.append(result_query)
            else:
                where_clauses.append(f' {key} = ?')
                params.append(value)

        where_query = ''
        if where_clauses:
            where_query = 'WHERE {}'.format(' AND '.join(where_clauses))
        query = query_template.format(where_query=where_query)
        return query, params
    
    def get_ads(self, dict_query=None, account_id=None):
        filters = {}
        if dict_query:
            filters.update(dict_query)
        if account_id:
            filters['seller.account_id'] = account_id
        
        query, params = self.build_ads_query(filters)
        cur = self.connection.execute(query, params)
        result = []
        list_ad_id = cur.fetchall()
        for ad_id in list_ad_id:
            result.append(self.phorm_dict_ad(ad_id[0]))
        return result

    def post_ad(self, request_json, account_id):
        
        cur = self.connection.cursor()
        title = request_json.get('title')
        tags = request_json.get('tags')
        dict_car = request_json.get('car')
        
        #Создаем сущность car,colors, images
        make = dict_car['make']
        model = dict_car['model']
        colors = dict_car['colors']
        num_owners = dict_car['num_owners']
        mileage = dict_car['mileage']
        reg_number = dict_car['reg_number']
        list_images = dict_car['images']


        cur.execute(
            'INSERT INTO car (make, model, mileage, reg_number, num_owners) '
            'VALUES (?, ?, ?, ?, ?)',
            (make, model, mileage, reg_number, num_owners,),
        )
        car_id = cur.lastrowid
        
        for elem in colors:
            cur.executescript(f"""
                PRAGMA foreign_keys = ON;
                INSERT INTO carcolor (color_id, car_id)
                VALUES ({elem}, {car_id})
            """)
        for image in list_images:
            title_image = image['title']
            url = image['url']
            cur.execute(
                'INSERT INTO image (title, url, car_id) '
                'VALUES (?, ?, ?)',
                (title_image, url, car_id,),
            )
            
        #Создаём сущность ad и tag
        cur.execute(f"""
            SELECT seller.id
            FROM seller
            WHERE seller.account_id={account_id}
        """)
        dict_seller = cur.fetchone()
        seller_id = dict_seller['id']
        date = datetime.datetime.utcnow()
        
        cur.execute(
            'INSERT INTO ad (title, date, seller_id, car_id) '
            'VALUES (?, ?, ?, ?)',
            (title, date, seller_id, car_id,),
        )
        ad_id = cur.lastrowid
        for elem in tags:
            elem = elem.lower()
            try:
                elem = elem.lower()
                cur.execute(
                    'INSERT INTO tag (name) '
                    'VALUES (?)',
                    (elem,),
                )
            except sqlite3.IntegrityError:
                pass
            query = (f"""
                    SELECT id
                    FROM tag
                    WHERE name=?
            """)
            cur.execute(query, (elem,))
            result = cur.fetchone()
            tag_id = result[0]
            cur.execute(
                'INSERT INTO adtag (tag_id, ad_id) '
                'VALUES (?, ?)',
                (tag_id, ad_id,),
            )
        self.connection.commit()
        ad = self.phorm_dict_ad(ad_id)
        return ad
    
    def patch_ad(self, request_json, ad_id):
        cur = self.connection.cursor()
        for key, value in request_json.items():
            if key == "title":
                query = (f"""
                            UPDATE ad
                            SET title = '{value}'
                            WHERE id= ?
                        """)
                cur.execute(query, (ad_id,))
            #Удаление старых связей adtag и создание новых тегов и связей
            elif key == "tags":
                cur.execute(f"""
                    DELETE
                    FROM adtag
                    WHERE adtag.ad_id={ad_id}
                        """)
                for tag in value:
                    tag = tag.lower()
                    try:
                        cur.execute(
                            'INSERT INTO tag (name) '
                            'VALUES (?)',
                            (tag,),
                        )
                    except sqlite3.IntegrityError:
                        pass
                    query = (f"""
                        SELECT id
                        FROM tag
                        WHERE name=?
                    """)
                    cur.execute(query, (tag,))
                    result = cur.fetchone()
                    tag_id = result[0]
                    cur.execute(
                        'INSERT INTO adtag (tag_id, ad_id) '
                        'VALUES (?, ?)',
                        (tag_id, ad_id,),
                    )
            elif key == 'car':
                cur.execute(f"""
                    SELECT car.id
                    FROM car
                        JOIN ad ON ad.car_id=car.id
                    WHERE ad.id={ad_id}
                """)
                result = cur.fetchone()
                car_id = result[0]
                for key_car, value_car in value.items():
                    # Удаление старых  и создание новых связей carcolor
                    if key_car == 'colors':
                        cur.execute(f"""
                            DELETE
                            FROM carcolor
                            WHERE carcolor.car_id={car_id}
                        """)
                        for color in value_car:
                            cur.execute(
                                'INSERT INTO carcolor (color_id, car_id) '
                                'VALUES (?, ?)',
                                (color, car_id,),
                            )
                    # Удаление старых картинок и создание новых записей по словарю
                    elif key_car == 'images':
                        cur.execute(f"""
                            DELETE
                            FROM image
                            WHERE image.car_id={car_id}
                        """)
                        for image in value_car:
                            cur.execute(
                                'INSERT INTO image (title, url, car_id) '
                                'VALUES (?, ?, ?)',
                                (image['title'], image['url'], car_id,),
                            )
                    else:
                        query = (f"""
                            UPDATE car
                            SET {key_car} = '{value_car}'
                            WHERE id= ?
                        """)
                        cur.execute(query, (car_id,))
        return
    
    def delete_ad(self, ad_id):
        cur = self.connection.cursor()
        cur.execute(f"""
            SELECT ad.car_id
            FROM ad
            WHERE ad.id={ad_id}
        """)
        result = cur.fetchone()
        car_id = result[0]
        
        cur.executescript(f"""
            PRAGMA foreign_keys = ON;
            DELETE
            FROM ad
            WHERE ad.id={ad_id}
        """)
        cur.executescript(f"""
            PRAGMA foreign_keys = ON;
            DELETE
            FROM car
            WHERE car.id={car_id}
        """)
        return
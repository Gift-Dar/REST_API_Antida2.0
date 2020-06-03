import sqlite3

from exceptions import ServiceError
from werkzeug.security import generate_password_hash


class UsersServiceError(ServiceError):
    service = 'users'


class UserDoesNotExistError(UsersServiceError):
    pass


class UsersService:
    def __init__(self, connection):
        self.connection = connection
    
    def reqistration_account(self, request_json):
        email = request_json.get('email')
        password = request_json.get('password')
        is_seller = request_json.get('is_seller')
        cur = self.connection.cursor()
        
        if not email or not password:
            return '', 400
        
        password_hash = generate_password_hash(password)
        first_name = request_json.get('first_name')
        last_name = request_json.get('last_name')
        
        try:
            cur.execute(
                "INSERT INTO account (email, password, first_name, last_name, is_seller) "
                "VALUES (?, ?, ?, ?, ?)",
                (email, password_hash, first_name, last_name, is_seller,),
            )
        
        except sqlite3.IntegrityError:
            return '', 409
        
        account_id = cur.lastrowid
        
        query = (
            'SELECT id, email, first_name, last_name, is_seller '
            'FROM account '
            'WHERE id=?'
        )
        cur = self.connection.execute(query, (account_id,))
        user = cur.fetchone()
        return user
    
    def registration_seller(self, request_json, account_id):
        zip_code = request_json.get('zip_code')
        phone = request_json.get('phone')
        city_id = request_json.get('city_id')
        home = request_json.get('home')
        street = request_json.get('street')
        cur = self.connection.cursor()
        
        if not zip_code or not phone or not city_id or not home or not street:
            return '', 400
        
        try:
            cur.executescript(f"""
                PRAGMA foreign_keys = ON;
                INSERT INTO  zipcode (zip_code, city_id)
                VALUES ({zip_code}, {city_id})
            """)
        except sqlite3.IntegrityError:
            pass
        
        cur.execute(
            'INSERT INTO seller (zip_code, street, home, phone, account_id) '
            'VALUES (?, ?, ?, ?, ?)',
            (zip_code, street, home, phone, account_id,),
        )
        
        query = ("""
            SELECT account.id, email, first_name, last_name, is_seller, phone, seller.zip_code, city_id, street, home
            FROM account
                JOIN seller ON account.id=seller.account_id
                JOIN zipcode ON seller.zip_code=zipcode.zip_code
            WHERE account.id=?
        """)
        cur.execute(query, (account_id,))
        result = cur.fetchone()
        return dict(result)
    
    def get_account(self, account_id):
        query = (
            'SELECT id, email, first_name, last_name, is_seller '
            'FROM account '
            'WHERE id=?'
        )
        params = (account_id,)
        cur = self.connection.execute(query, params)
        account = cur.fetchone()
        if account is None:
            raise UserDoesNotExistError(account_id)
        
        query_seller = (
            'SELECT is_seller '
            'FROM account '
            'WHERE account.id=?'
        )
        cur = self.connection.execute(query_seller, params)
        is_seller = cur.fetchone()
        if bool(is_seller[0]):
            query = (
                'SELECT account.id, email, first_name, last_name, is_seller, phone, seller.zip_code, city_id, street, home '
                'FROM account JOIN seller ON account.id=seller.account_id JOIN zipcode ON seller.zip_code=zipcode.zip_code '
                'WHERE account.id = ?'
            )
            cur = self.connection.execute(query, params)
            account = cur.fetchone()
        return dict(account)
    
    def patch_account(self, request_json, account_id):
        cur = self.connection.cursor()
        
        for key, value in request_json.items():
            if key == "first_name" or key == "last_name":
                query = (f"""
                    UPDATE account
                    SET {key} = '{value}'
                    WHERE id= ?
                """)
                cur.execute(query, (account_id,))
            
            elif key == 'is_seller':
                if value:
                    query = (f"""
                        UPDATE account
                        SET is_seller = true
                        WHERE id= ?
                    """)
                    cur.execute(query, (account_id,))
                    user_patch = self.registration_seller(request_json, account_id)
                    return user_patch
                else:
                    cur.execute(f"""
                        SELECT car.id
                        FROM car
                            JOIN ad ON car.id=ad.car_id
                        WHERE ad.seller_id = (
                            SELECT seller.id
                            FROM seller
                            WHERE seller.account_id={account_id}
                        )
                    ;""")
                    result = cur.fetchall()
                    list_car = []
                    for u in result:
                        list_car.append(u[0])

                    cur.executescript(f"""
                        PRAGMA foreign_keys = ON;
                        DELETE
                        FROM seller
                        WHERE seller.account_id={account_id}
                    """)
                    
                    for elem in list_car:
                        cur.executescript(f"""
                            PRAGMA foreign_keys = ON;
                            DELETE
                            FROM car
                            WHERE car.id={elem}
                        """)

                    query = (f"""
                        UPDATE account
                        SET is_seller = false
                        WHERE account.id= ?
                    """)
                    cur.execute(query, (account_id,))
                    return '', 204
            else:
                query = (f"""
                    UPDATE seller
                    SET {key} = '{value}'
                    WHERE id= ?
                """)
                cur.execute(query, (account_id,))
                
        query = (
            'SELECT is_seller '
            'FROM account '
            'WHERE id=?'
        )
        cur.execute(query, (account_id,))
        result = cur.fetchone()
        is_seller = result[0]
        if is_seller:
            query = ("""
                SELECT account.id, email, first_name, last_name, is_seller, phone, seller.zip_code, city_id, street, home
                FROM account
                    JOIN seller ON account.id=seller.account_id
                    JOIN zipcode ON seller.zip_code=zipcode.zip_code
                WHERE account.id=?
            """)
            cur.execute(query, (account_id,))
            result = cur.fetchone()
            return dict(result)
        else:
            query = (
                'SELECT id, email, first_name, last_name, is_seller '
                'FROM account '
                'WHERE id=?'
            )
            cur.execute(query, (account_id,))
            result = cur.fetchone()
            return dict(result)
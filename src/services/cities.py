import sqlite3

from exceptions import ServiceError


class CitiesServiceError(ServiceError):
    service = 'ads'


class CityDoesNotExistError(CitiesServiceError):
    pass


class CitiesService:
    def __init__(self, connection):
        self.connection = connection
        
    def get_cities(self):
        cur = self.connection.execute(
            'SELECT id, name '
            'FROM city'
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def post_city(self, request_json):
        name_city = request_json.get('name')
    
        if not name_city:
            return '', 400
        query = (
            'SELECT id, name '
            'FROM city '
            'WHERE name = ?'
        )
        try:
            self.connection.execute(
                'INSERT INTO city (name) '
                'VALUES (?)',
                (name_city,),
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            cur = self.connection.execute(query, (name_city,))
            city = cur.fetchone()
            return dict(city)
    
        cur = self.connection.execute(query, (name_city,))
        city = cur.fetchone()
        return dict(city)
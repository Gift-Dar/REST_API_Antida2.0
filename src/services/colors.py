import sqlite3

from exceptions import ServiceError


class ColorsServiceError(ServiceError):
    service = 'ads'


class ColorDoesNotExistError(ColorsServiceError):
    pass


class ColorsService:
    def __init__(self, connection):
        self.connection = connection
    
    def get_colors(self):
        cur = self.connection.execute(
            'SELECT id, name, hex '
            'FROM color'
        )
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    
    def post_color(self, request_json):
        name_color = request_json.get('name')
        hex = request_json.get('hex')
    
        if not name_color or not hex:
            return '', 400
    
        query = (
            'SELECT name, hex '
            'FROM color '
            'WHERE name = ?'
        )
    
        try:
            self.connection.execute(
                'INSERT INTO color (name,hex) '
                'VALUES (?, ?)',
                (name_color, hex,),
            )
            self.connection.commit()
        except sqlite3.IntegrityError:
            cur = self.connection.execute(query, (name_color,))
            color = cur.fetchone()
            return dict(color)
    
        cur = self.connection.execute(query, (name_color,))
        color = cur.fetchone()
        return dict(color)
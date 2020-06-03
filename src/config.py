import os


class Config:
    DB_CONNECTION = os.getenv('DB_CONNECTION', 'db.sqlite')
    SECRET_KEY = b'156fddgdfg15565616'
    UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Images'))
import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(256)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.urandom(256)
    CLOUDSQL_USER = 'root'
    CLOUDSQL_PASSWORD = 'hax4D3People!'
    CLOUDSQL_DATABASE = 'hackforthepeople'
    CLOUDSQL_CONNECTION_NAME = 'hackforthepeople:us-central1:hftp'

    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://{nm}:{pw}@35.238.58.159/{db}').format (
        nm=CLOUDSQL_USER,
        pw=CLOUDSQL_PASSWORD,
        db=CLOUDSQL_DATABASE,
    )
# database_config.py
# TODO: change the database ?

import os


# Set the variables

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_DB_NEW = os.getenv("POSTGRES_DB_NEW")
POSTGRES_DB_NEW_USER = os.getenv("POSTGRES_DB_NEW_USER")
FILESTORE_PASSSWORD = os.getenv("FILESTORE_PASSSWORD")

DB_URL = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(user=POSTGRES_USER,password=POSTGRES_PASSWORD,host=POSTGRES_HOST,port=POSTGRES_PORT,database=POSTGRES_DB)
BIND_URL = 'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'.format(user=POSTGRES_DB_NEW_USER,password=FILESTORE_PASSSWORD,host=POSTGRES_HOST,port=POSTGRES_PORT,database=POSTGRES_DB_NEW)

# Sets the database
class Config(object):
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'butter'
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_BINDS = {'two': BIND_URL}
    SQLALCHEMY_TRACK_MODIFICATIONS = False


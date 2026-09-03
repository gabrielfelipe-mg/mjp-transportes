import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')

SGBD = os.getenv('DB_SGBD')
usuario = os.getenv('DB_USER')
senha = os.getenv('DB_PASSWORD')
servidor = os.getenv('DB_HOST')
database = os.getenv('DB_NAME')

SQLALCHEMY_DATABASE_URI = f"{SGBD}://{usuario}:{senha}@{servidor}/{database}"
# E:\projeto\pescaria2.0\config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua-chave-secreta-forte-aqui'
    # Configurações do banco de dados
    DB_HOST = 'localhost'
    DB_USER = 'root'
    DB_PASSWORD = '123456'
    DB_NAME = 'pescaria'

    # URI de conexão com o MySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
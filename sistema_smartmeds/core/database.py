import mysql.connector
from mysql.connector import Error

from config import DB_CONFIG


class Database:
    @staticmethod
    def connect():
        try:
            return mysql.connector.connect(**DB_CONFIG)
        except Error as erro:
            raise RuntimeError(
                f"Falha na conexão com o banco de dados ({DB_CONFIG['host']}/"
                f"{DB_CONFIG['database']}): {erro}"
            ) from erro

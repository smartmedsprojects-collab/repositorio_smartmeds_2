from core.crud_base import CrudBase
from core.database import Database
from core.security import verificar_senha


class Usuario(CrudBase):

    table = "usuario"

    fields = ["nome", "email", "senha", "tipo", "identificacao"]

    def __init__(self, nome, email, senha, tipo, identificacao):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo
        self.identificacao = identificacao

    @classmethod
    def autenticar(cls, email, senha):

        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:

            sql = """
                SELECT *
                FROM usuario
                WHERE email = %s
            """

            cursor.execute(sql, (email,))
            usuario = cursor.fetchone()

            if not usuario:
                return None

            if verificar_senha(senha, usuario["senha"]):
                return usuario

            return None

        finally:
            cursor.close()
            conexao.close()

from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Localizacao(CrudBase):

    table = "localizacao"

    fields = ["rua", "numero", "andar", "usuario_id"]

    def __init__(self, rua, numero, andar, usuario_id):
        self.rua = rua
        self.numero = numero
        self.andar = andar
        self.usuario_id = int(usuario_id) if usuario_id else None

    def validate(self):

        erros = [
            Validator.required(self.rua, "Rua"),
            Validator.required(self.numero, "Número"),
            Validator.required(self.andar, "Andar"),
            Validator.required(self.usuario_id, "Usuário"),
        ]

        return [erro for erro in erros if erro]

    @classmethod
    def find_all_by_usuario(cls, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM localizacao
                WHERE usuario_id = %s
                ORDER BY rua
            """
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
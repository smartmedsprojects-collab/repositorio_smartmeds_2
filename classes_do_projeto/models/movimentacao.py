from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Movimentacao(CrudBase):
    table = "movimentacao"

    fields = [
        "tipo",
        "quantidade",
        "data_movimentacao",
        "observacao",
        "produto_id"
    ]

    def __init__(
        self,
        tipo,
        quantidade,
        produto_id,
        data_movimentacao=None,
        observacao=None
    ):
        self.tipo = tipo
        self.quantidade = int(quantidade) if quantidade else 0
        self.produto_id = int(produto_id) if produto_id else None
        self.data_movimentacao = data_movimentacao
        self.observacao = observacao

    def validate(self):
        erros = [
            Validator.required(self.tipo, "Tipo"),
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.produto_id, "Produto"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_all(cls, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT m.*
                FROM {cls.table} m
                ORDER BY m.id DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_all_with_product(cls, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT 
                    m.*,
                    p.nome AS produto_nome,
                    p.marca AS produto_marca
                FROM movimentacao m
                INNER JOIN produto p ON p.id = m.produto_id
                ORDER BY m.id DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
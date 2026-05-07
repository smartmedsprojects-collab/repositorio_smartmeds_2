from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

class ItemEntrada(CrudBase):
    table = "item_entrada"
    fields = [
        "quantidade",
        "valor",
        "pedido_entrada_id",
        "estoque_id"
    ]

    def __init__(self, quantidade, valor, pedido_entrada_id, estoque_id):
        self.quantidade = quantidade
        self.valor = valor
        self.pedido_entrada_id = pedido_entrada_id
        self.estoque_id = estoque_id

    def validate(self):
        erros = [
            Validator.required(self.pedido_entrada_id, "pedido de entrada"),
            Validator.required(self.estoque_id, "estoque"),
            Validator.non_negative(self.valor, "valor")
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_pedido(cls, pedido_entrada_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT * FROM item_entrada 
                WHERE pedido_entrada_id = %s 
                ORDER BY id
            """
            cursor.execute(sql, (pedido_entrada_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        # Normalmente item_entrada não depende de outras tabelas
        # mas mantido para padrão do projeto
        return False

    @classmethod
    def safe_delete(cls, id):
        item = cls.find_by_id(id)
        if not item:
            raise ValueError("Item de entrada não encontrado.")
        cls.delete(id)
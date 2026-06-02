from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

class ItemSaida(CrudBase):
    table = "item_saida"
    fields = [
        "quantidade",
        "valor",
        "Pedido_saida_id",
        "estoque_id"
    ]

    def __init__(self, quantidade, valor, Pedido_saida_id, estoque_id):
        self.quantidade = quantidade
        self.valor = valor
        self.Pedido_saida_id = Pedido_saida_id
        self.estoque_id = estoque_id

    def validate(self):
        erros = [
            Validator.required(self.Pedido_saida_id, "pedido de saída"),
            Validator.required(self.estoque_id, "estoque"),
            Validator.non_negative(self.valor, "valor"),
            Validator.required(self.quantidade, "Quantidade"),
            Validator.non_negative(self.quantidade, "Quantidade")
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_pedido(cls, Pedido_saida_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT * FROM item_saida 
                WHERE Pedido_saida_id = %s 
                ORDER BY id
            """
            cursor.execute(sql, (Pedido_saida_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        # Seguindo o padrão, normalmente não há dependências diretas
        return False

    @classmethod
    def safe_delete(cls, id):
        item = cls.find_by_id(id)
        if not item:
            raise ValueError("Item de saída não encontrado.")
        cls.delete(id)
from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class ItemSaida(CrudBase):

    table = "item_saida"

    fields = ["quantidade", "valor", "pedido_saida_id", "produto_id"]

    def __init__(self, quantidade, valor, pedido_saida_id, movimentacao_id):
        self.quantidade = int(quantidade)
        self.valor = float(valor)
        self.pedido_saida_id = int(pedido_saida_id)
        self.movimentacao_id = int(movimentacao_id)

    def validate(self):
        erros = [
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.valor, "Valor"),
            Validator.required(self.pedido_saida_id, "Pedido"),
            Validator.required(self.movimentacao_id, "Movimentação"),
        ]
    return [erro for erro in erros if erro]
       
    @classmethod
    def find_by_pedido(cls, pedido_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT
                    i.id,
                    i.quantidade,
                    i.valor,
                    p.nome AS produto,
                    p.id AS produto_id
                FROM item_saida i
                INNER JOIN movimentacao m
                    ON i.movimentacao_id = m.id
                INNER JOIN produto p
                    ON m.produto_id = p.id
                WHERE i.pedido_saida_id = %s
            """
            cursor.execute(sql, (pedido_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
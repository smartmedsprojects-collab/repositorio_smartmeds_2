from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class ItemSaida(CrudBase):

    table = "item_saida"

    fields = ["quantidade", "valor", "pedido_saida_id", "produto_id"]

    def __init__(self, quantidade, valor, pedido_saida_id, produto_id):
        self.quantidade = int(quantidade)
        self.valor = float(valor)
        self.pedido_saida_id = int(pedido_saida_id)
        self.produto_id = int(produto_id)

    def validate(self):

        erros = [
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.valor, "Valor"),
            Validator.required(self.pedido_saida_id, "Pedido"),
            Validator.required(self.produto_id, "Produto"),
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
                    p.nome AS produto
                FROM item_saida i
                INNER JOIN produto p
                    ON i.produto_id = p.id
                WHERE i.pedido_saida_id = %s
            """

            cursor.execute(sql, (pedido_id,))
            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

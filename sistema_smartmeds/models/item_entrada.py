from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class ItemEntrada(CrudBase):
    table = "item_entrada"
    fields = ["quantidade", "valor", "pedido_entrada_id", "movimentacao_id"]

    def __init__(self, quantidade, valor, pedido_entrada_id, movimentacao_id=None):
        try:
            self.quantidade = int(quantidade)
        except (TypeError, ValueError):
            self.quantidade = 0
        try:
            self.valor = float(str(valor).replace(",", ".")) if valor not in (None, "") else None
        except (TypeError, ValueError):
            self.valor = None
        self.pedido_entrada_id = int(pedido_entrada_id) if pedido_entrada_id not in (None, "", 0, "0") else None
        self.movimentacao_id = int(movimentacao_id) if movimentacao_id not in (None, "", 0, "0") else None

    def validate(self):
        erros = [
            Validator.min_value(self.quantidade, "Quantidade", 50),
            Validator.non_negative(self.valor, "Valor"),
            Validator.required(self.pedido_entrada_id, "Pedido"),
            Validator.required(self.movimentacao_id, "Movimentação"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_pedido(cls, pedido_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT ie.id, ie.quantidade, ie.valor, ie.movimentacao_id,
                       p.nome AS produto
                FROM item_entrada ie
                INNER JOIN movimentacao m ON ie.movimentacao_id = m.id
                INNER JOIN produto p ON m.produto_id = p.id
                WHERE ie.pedido_entrada_id = %s
                ORDER BY ie.id
            """
            cursor.execute(sql, (pedido_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

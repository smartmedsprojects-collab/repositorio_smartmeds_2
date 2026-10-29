from math import isfinite

from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class ItemSaida(CrudBase):
    table = "item_saida"
    fields = ["quantidade", "valor", "pedido_saida_id", "movimentacao_id"]

    def __init__(self, quantidade, valor, pedido_saida_id, movimentacao_id=None):
        try:
            self.quantidade = int(quantidade)
        except (TypeError, ValueError):
            self.quantidade = 0
        try:
            self.valor = float(str(valor).replace(",", ".")) if valor not in (None, "") else None
        except (TypeError, ValueError):
            self.valor = None
        self.pedido_saida_id = int(pedido_saida_id) if pedido_saida_id not in (None, "", 0, "0") else None
        self.movimentacao_id = int(movimentacao_id) if movimentacao_id not in (None, "", 0, "0") else None

    def validate(self):
        erros = [
            Validator.positive(self.quantidade, "Quantidade"),
            Validator.non_negative(self.valor, "Valor"),
            Validator.required(self.pedido_saida_id, "Pedido"),
            Validator.required(self.movimentacao_id, "Movimentação"),
        ]
        if self.valor is not None and not isfinite(self.valor):
            erros.append("O campo Valor deve ser um número válido.")
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_pedido(cls, pedido_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT i.id, i.quantidade, i.valor, i.movimentacao_id,
                       p.nome AS produto
                FROM item_saida i
                INNER JOIN movimentacao m ON i.movimentacao_id = m.id
                INNER JOIN produto p ON m.produto_id = p.id
                WHERE i.pedido_saida_id = %s
                ORDER BY i.id
            """
            cursor.execute(sql, (pedido_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

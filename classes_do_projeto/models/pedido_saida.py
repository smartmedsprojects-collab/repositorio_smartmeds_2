from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

class PedidoSaida(CrudBase):

    table = "pedido_saida"

    fields = [
        "tipo",
        "pagamento",
        "quantidade",
        "valor",
        "data_pagamento",
        "cliente_id",
        "usuario_id",
    ]

    def __init__(
        self,
        tipo,
        pagamento,
        quantidade,
        valor,
        data_pagamento,
        cliente_id,
        usuario_id,
    ):
        self.tipo = tipo.strip()
        self.pagamento = pagamento.strip()
        self.quantidade = int(quantidade)
        self.valor = float(valor)
        self.data_pagamento = data_pagamento
        self.cliente_id = int(cliente_id)
        self.usuario_id = int(usuario_id)

    def validate(self):
        erros = [
            Validator.required(self.tipo, "Tipo"),
            Validator.required(self.pagamento, "Pagamento"),
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.valor, "Valor"),
            Validator.required(
                self.data_pagamento,
                "Data de pagamento"
            ),
            Validator.required(self.cliente_id, "Cliente"),
            Validator.required(self.usuario_id, "Usuário"),
        ]

        return [erro for erro in erros if erro]

    @classmethod
    def listar_pedidos(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            sql = """
                SELECT
                    ps.*,
                    c.nome AS cliente,
                    u.nome AS usuario
                FROM pedido_saida ps
                LEFT JOIN cliente c
                    ON ps.cliente_id = c.id
                LEFT JOIN usuario u
                    ON ps.usuario_id = u.id
                ORDER BY ps.id DESC
            """

            cursor.execute(sql)

            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def listar_movimentacoes(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            sql = """
                SELECT
                    ps.id,
                    ps.tipo,
                    ps.pagamento,
                    ps.quantidade,
                    ps.valor,
                    ps.data_pagamento,
                    c.nome AS cliente,
                    u.nome AS usuario
                FROM pedido_saida ps
                LEFT JOIN cliente c
                    ON ps.cliente_id = c.id
                LEFT JOIN usuario u
                    ON ps.usuario_id = u.id
                ORDER BY ps.id DESC
            """

            cursor.execute(sql)

            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

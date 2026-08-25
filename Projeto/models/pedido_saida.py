from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class PedidoSaida(CrudBase):

    table = "pedido_saida"

    fields = [
        "tipo",
        "pagamento",
        "data_pagamento",
        "cliente_id",
        "usuario_id",
    ]

    def __init__(
        self,
        tipo,
        pagamento,
        data_pagamento,
        cliente_id,
        usuario_id,
    ):
        self.tipo = tipo.strip()
        self.pagamento = pagamento.strip()
        self.data_pagamento = data_pagamento
        self.cliente_id = int(cliente_id)
        self.usuario_id = int(usuario_id)

    def validate(self):

        erros = [
            Validator.required(self.tipo, "Tipo"),
            Validator.required(self.pagamento, "Pagamento"),
            Validator.required(self.data_pagamento, "Data de pagamento"),
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
                    ps.tipo,
                    c.nome AS cliente,
                    u.nome AS usuario,
                    ps.pagamento,
                    ps.data_pagamento
                FROM pedido_saida ps
                LEFT JOIN cliente c
                    ON ps.cliente_id = c.id
                LEFT JOIN usuario u
                    ON ps.usuario_id = u.id
                ORDER BY ps.data_pagamento DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
    
    @classmethod
    def has_related_records(cls, pedido_id):
        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
            sql = """
                SELECT COUNT(*)
                FROM item_saida
                WHERE pedido_saida_id = %s
            """

            cursor.execute(sql, (pedido_id,))
            resultado = cursor.fetchone()

            return resultado[0] > 0

        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, pedido_id):
        pedido = cls.find_by_id(pedido_id)

        if not pedido:
            raise ValueError(
                "Pedido de saída não encontrado."
            )

        if cls.has_related_records(pedido_id):
            raise ValueError(
                "Não é possível excluir o pedido de saída "
                "porque existem itens vinculados."
            )

        return cls.delete(pedido_id)

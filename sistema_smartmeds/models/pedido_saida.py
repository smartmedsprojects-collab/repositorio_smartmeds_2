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
        tipo=None,
        pagamento=None,
        quantidade=None,
        valor=None,
        data_pagamento=None,
        cliente_id=None,
        usuario_id=None,
        **kwargs  # Garante compatibilidade caso o CrudBase passe outros atributos
    ):
        self.tipo = tipo.strip() if isinstance(tipo, str) else tipo
        self.pagamento = pagamento.strip() if isinstance(pagamento, str) else pagamento
        
        # Conversão segura para int/float
        try:
            self.quantidade = int(quantidade) if quantidade is not None and quantidade != "" else None
        except (ValueError, TypeError):
            self.quantidade = quantidade

        try:
            self.valor = float(valor) if valor is not None and valor != "" else None
        except (ValueError, TypeError):
            self.valor = valor

        self.data_pagamento = data_pagamento

        try:
            self.cliente_id = int(cliente_id) if cliente_id is not None and cliente_id != "" else None
        except (ValueError, TypeError):
            self.cliente_id = cliente_id

        try:
            self.usuario_id = int(usuario_id) if usuario_id is not None and usuario_id != "" else None
        except (ValueError, TypeError):
            self.usuario_id = usuario_id

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
    def listar_pedidos(cls, usuario_id):
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
                WHERE ps.usuario_id = %s
                ORDER BY ps.id DESC
            """

            cursor.execute(sql, (usuario_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def listar_movimentacoes(cls, usuario_id):
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
                WHERE ps.usuario_id = %s
                ORDER BY ps.id DESC
            """

            cursor.execute(sql, (usuario_id,))

            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()
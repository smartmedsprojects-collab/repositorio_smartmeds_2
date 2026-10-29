from math import isfinite

from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class PedidoSaida(CrudBase):
    table = "pedido_saida"
    fields = ["tipo", "pagamento", "quantidade", "valor", "data_pagamento", "cliente_id", "usuario_id"]

    def __init__(
        self,
        tipo=None,
        pagamento=None,
        quantidade=None,
        valor=None,
        data_pagamento=None,
        cliente_id=None,
        usuario_id=None,
        **kwargs,
    ):
        self.tipo = tipo.strip().upper() if isinstance(tipo, str) else tipo
        self.pagamento = pagamento.strip().upper() if isinstance(pagamento, str) else pagamento
        try:
            self.quantidade = int(quantidade) if quantidade not in (None, "") else None
        except (ValueError, TypeError):
            self.quantidade = None
        try:
            self.valor = float(str(valor).replace(",", ".")) if valor not in (None, "") else None
        except (ValueError, TypeError):
            self.valor = None
        self.data_pagamento = data_pagamento
        try:
            self.cliente_id = int(cliente_id) if cliente_id not in (None, "", 0, "0") else None
        except (ValueError, TypeError):
            self.cliente_id = None
        try:
            self.usuario_id = int(usuario_id) if usuario_id not in (None, "", 0, "0") else None
        except (ValueError, TypeError):
            self.usuario_id = None

    def validate(self):
        erros = [
            Validator.required(self.tipo, "Tipo"),
            Validator.required(self.pagamento, "Pagamento"),
            Validator.positive(self.quantidade, "Quantidade"),
            Validator.non_negative(self.valor, "Valor"),
            Validator.required(self.data_pagamento, "Data de pagamento"),
            Validator.date(self.data_pagamento, "Data de pagamento"),
            Validator.required(self.cliente_id, "Cliente"),
            Validator.required(self.usuario_id, "Usuário"),
        ]
        if self.valor is not None and not isfinite(self.valor):
            erros.append("O valor deve ser um número válido.")
        if self.tipo and self.tipo not in {"VENDA", "DOACAO", "DESCARTE"}:
            erros.append("O tipo do pedido de saída é inválido.")
        if self.pagamento and self.pagamento not in {"DINHEIRO", "PIX", "CARTAO", "BOLETO"}:
            erros.append("A forma de pagamento é inválida.")
        return [erro for erro in erros if erro]

    @classmethod
    def listar_pedidos(cls, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT ps.*, c.nome AS cliente, u.nome AS usuario
                FROM pedido_saida ps
                LEFT JOIN cliente c ON ps.cliente_id = c.id AND c.usuario_id = ps.usuario_id
                LEFT JOIN usuario u ON ps.usuario_id = u.id
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
        return cls.listar_pedidos(usuario_id)

    @classmethod
    def safe_delete(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = "SELECT id FROM pedido_saida WHERE id = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            sql += " FOR UPDATE"
            cursor.execute(sql, tuple(parametros))
            if not cursor.fetchone():
                raise ValueError("Pedido de saída não encontrado ou acesso negado.")

            cursor.execute("SELECT COUNT(*) FROM item_saida WHERE pedido_saida_id = %s", (id,))
            if cursor.fetchone()[0]:
                raise ValueError(
                    "Não é possível excluir este pedido porque existem itens de saída vinculados."
                )

            sql = "DELETE FROM pedido_saida WHERE id = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

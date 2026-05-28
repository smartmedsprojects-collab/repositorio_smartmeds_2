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
        "produto_id"
    ]
    def __init__(self, tipo, pagamento, quantidade, valor, data_pagamento, cliente_id, usuario_id, produto_id, id=None):
        self.id = id
        self.tipo = tipo
        self.pagamento = pagamento
        self.quantidade = quantidade
        self.valor = valor
        self.data_pagamento = data_pagamento
        self.cliente_id = cliente_id
        self.usuario_id = usuario_id
        self.produto_id = produto_id
        
    def validate(self):
        erros = [
            Validator.required(self.tipo, "Tipo"),
            Validator.required(self.pagamento, "Pagamento"),
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.valor, "Valor"),
            Validator.required(self.data_pagamento,"Data de pagamento"),
            Validator.date(self.data_pagamento,"Data de pagamento"),
            Validator.required(self.cliente_id,"Cliente"),
            Validator.required(self.usuario_id,"Usuário"),
            Validator.required(self.produto_id,"Produto"),
        ]
        return [erro for erro in erros if erro]
    @classmethod
    def find_all(cls, order_by="id DESC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT * FROM {cls.table}
                ORDER BY {order_by}
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
    @classmethod
    def find_by_tipo(cls, tipo):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT * FROM {cls.table}
                WHERE tipo LIKE %s
                ORDER BY id DESC
            """
            cursor.execute(sql, (f"%{tipo}%",))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()
    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            queries = [
                "SELECT COUNT(*) FROM item_saida WHERE pedido_saida_id = %s"
            ]
            total = 0
            for sql in queries:
                cursor.execute(sql, (id,))
                total += cursor.fetchone()[0]
            return total > 0
        finally:
            cursor.close()
            conexao.close()
    @classmethod
    def safe_delete(cls, id):
        pedido_saida = cls.find_by_id(id)
        if not pedido_saida:
            raise ValueError(
                "Pedido de saída não encontrado.")
        if cls.has_related_records(id):
            raise ValueError(
                "Não é possível excluir o pedido "
                "porque existem registros vinculados.")
        return cls.delete(id)
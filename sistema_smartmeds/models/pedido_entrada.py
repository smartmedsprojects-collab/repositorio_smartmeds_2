from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class PedidoEntrada(CrudBase):
    table = "pedido_entrada"
    pk = "id_pedido_entrada"

    fields = [
        "numero_documento",
        "fornecedor",
        "data_entrada",
        "usuario_id", 
        "observacao",
        "status",
    ]

    def __init__(
        self, numero_documento, fornecedor, data_entrada, usuario_id, observacao, status
    ):
        self.numero_documento = numero_documento.strip()
        self.fornecedor = fornecedor.strip()
        self.data_entrada = data_entrada
        self.usuario_id = int(usuario_id) if usuario_id else None
        self.observacao = observacao.strip()
        self.status = status.strip()

    def validate(self):
        erros = [
            Validator.required(self.numero_documento, "Número do documento"),
            Validator.required(self.fornecedor, "Fornecedor"),
            Validator.required(self.data_entrada, "Data de entrada"),
            Validator.required(self.usuario_id, "Usuário"),  # Corrigido: usuario_id
            Validator.required(self.status, "Status"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def listar_movimentacoes(cls, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:
            sql = """
                SELECT
                    pe.id_pedido_entrada,
                    pe.numero_documento,
                    pe.fornecedor,
                    pe.data_entrada,
                    pe.observacao,
                    pe.status,
                    u.nome AS usuario
                FROM pedido_entrada pe
                LEFT JOIN usuario u
                    ON pe.usuario_id = u.id
                WHERE pe.usuario_id = %s
                ORDER BY pe.data_entrada DESC
            """  # Corrigido: pe.usuario_id no JOIN e no WHERE

            cursor.execute(sql, (usuario_id,))
            return cursor.fetchall()

        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        return False

    @classmethod
    def safe_delete(cls, id):
        pedido = cls.find_by_id(id)
        if not pedido:
            raise ValueError("Pedido de entrada não encontrado.")
        return cls.delete(id)
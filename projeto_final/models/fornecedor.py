from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator
from core.security import gerar_hash_senha
from models.pedido_entrada import PedidoEntrada

class Fornecedor(CrudBase):
    table = "fornecedor"

    fields = [
        "nome",
        "email",
        "senha",
        "cnpj",
        "usuario_id"
    ]

    def __init__(self, nome, email, senha, cnpj, usuario_id):
        self.nome = nome.strip()
        self.email = email.strip().lower()
        self.senha = senha.strip()
        self.cnpj = "".join(filter(str.isdigit, str(cnpj or "")))
        self.usuario_id = int(usuario_id) if usuario_id else None

    def validate(self):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.only_letters(self.nome, "Nome"),
            Validator.required(self.email, "Email"),
            Validator.email(self.email),
            Validator.required(self.senha, "Senha"),
            Validator.min_length(self.senha, "Senha", 8),
            Validator.required(self.cnpj, "CNPJ"),
            Validator.cnpj(self.cnpj),
            Validator.required(self.usuario_id, "Usuário")
        ]
        return [erro for erro in erros if erro]

    def insert(self):
        self.senha = gerar_hash_senha(self.senha)
        return super().insert()

    @classmethod
    def find_all_by_usuario(cls, usuario_id, order_by="nome ASC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT *
                FROM fornecedor
                WHERE usuario_id = %s
                ORDER BY {order_by}
            """
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_nome(cls, nome, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM fornecedor
                WHERE nome LIKE %s AND usuario_id = %s
                ORDER BY nome
            """
            cursor.execute(sql, (f"%{nome}%", usuario_id))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_email(cls, email, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM fornecedor
                WHERE email = %s AND usuario_id = %s
            """
            cursor.execute(sql, (email, usuario_id))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = "SELECT nome, usuario_id FROM fornecedor WHERE id = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            fornecedor = cursor.fetchone()
            if not fornecedor:
                raise ValueError("Fornecedor não encontrado ou acesso negado.")

            # O pedido de entrada guarda o nome do fornecedor, não um fornecedor_id.
            coluna_usuario_pedido = PedidoEntrada.coluna_usuario(cursor)
            sql = (
                f"SELECT COUNT(*) AS total FROM pedido_entrada "
                f"WHERE fornecedor = %s AND {coluna_usuario_pedido} = %s"
            )
            cursor.execute(sql, (fornecedor["nome"], fornecedor["usuario_id"]))
            return cursor.fetchone()["total"] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id, usuario_id=None):
        if not cls.find_by_id(id, usuario_id=usuario_id):
            raise ValueError("Fornecedor não encontrado ou acesso negado.")
        if cls.has_related_records(id, usuario_id=usuario_id):
            raise ValueError("Não é possível excluir o fornecedor porque existem pedidos de entrada com esse nome.")
        return cls.delete(id, usuario_id=usuario_id)

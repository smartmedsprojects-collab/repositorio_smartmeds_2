from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

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
        self.cnpj = cnpj.strip()
        self.usuario_id = int(usuario_id) if usuario_id else None

    def validate(self):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.only_letters(self.nome, "Nome"),
            Validator.required(self.email, "Email"),
            Validator.email(self.email),
            Validator.required(self.senha, "Senha"),
            Validator.min_length(self.senha, "Senha", 6),
            Validator.required(self.cnpj, "CNPJ"),
            Validator.cnpj(self.cnpj),
            Validator.required(self.usuario_id, "Usuário")
        ]
        return [erro for erro in erros if erro]

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
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            queries = [
                """
                SELECT COUNT(*)
                FROM pedido_entrada
                WHERE fornecedor_id = %s
                """
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
        fornecedor = cls.find_by_id(id)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado.")
        if cls.has_related_records(id):
            raise ValueError("Não é possível excluir o fornecedor porque existem registros vinculados.")
        return cls.delete(id)
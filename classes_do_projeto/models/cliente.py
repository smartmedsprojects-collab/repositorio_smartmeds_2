from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

class Cliente(CrudBase):
    table = "cliente"
    fields = ["nome", "email", "senha", "cnpj"]

    def __init__(self, nome, email, senha, cnpj):
        self.nome = nome.strip()
        self.email = email.strip().lower()
        self.senha = senha.strip()
        self.cnpj = cnpj.strip()

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
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_nome(cls, nome):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM cliente
                WHERE nome LIKE %s
                ORDER BY nome
            """
            cursor.execute(sql, (f"%{nome}%",))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_email(cls, email):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT *
                FROM cliente
                WHERE email = %s
            """
            cursor.execute(sql, (email,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                SELECT COUNT(*)
                FROM pedido_saida
                WHERE cliente_id = %s
            """
            cursor.execute(sql, (id,))
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            cliente = cls.find_by_id(id)
            if not cliente:
                raise ValueError("Cliente não encontrado.")
            cursor.execute(
                """
                SELECT id
                FROM pedido_saida
                WHERE cliente_id = %s
                """,
                (id,),
            )
            pedidos = cursor.fetchall()
            for pedido in pedidos:
                pedido_id = pedido[0]
                cursor.execute(
                    """
                    SELECT movimentacao_id
                    FROM item_saida
                    WHERE pedido_saida_id = %s
                    """,
                    (pedido_id,),
                )
                movimentacoes = cursor.fetchall()
                cursor.execute(
                    """
                    DELETE FROM item_saida
                    WHERE pedido_saida_id = %s
                    """,
                    (pedido_id,),
                )
                for movimentacao in movimentacoes:
                    movimentacao_id = movimentacao[0]
                    if movimentacao_id:
                        cursor.execute(
                            """
                            DELETE FROM movimentacao
                            WHERE id = %s
                            """,
                            (movimentacao_id,),
                        )
                cursor.execute(
                    """
                    DELETE FROM pedido_saida
                    WHERE id = %s
                    """,
                    (pedido_id,),
                )
            cursor.execute(
                """
                DELETE FROM cliente
                WHERE id = %s
                """,
                (id,),
            )
            if cursor.rowcount == 0:
                raise ValueError("Cliente não encontrado.")
            conexao.commit()
            return True
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()
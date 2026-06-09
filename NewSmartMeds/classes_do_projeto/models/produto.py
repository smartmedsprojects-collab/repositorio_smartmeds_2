from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Produto(CrudBase):
    table = "produto"
    fields = [
        "nome",
        "marca",
        "data_de_validade",
        "especificacao",
        "unidade_medida",
    ]

    def __init__(self, nome, marca, data_de_validade, especificacao, unidade_medida):
        self.nome = nome
        self.marca = marca
        self.data_de_validade = data_de_validade
        self.especificacao = especificacao
        self.unidade_medida = unidade_medida

    def validate(self):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.required(self.marca, "Marca"),
            Validator.min_length(self.marca, "Marca", 2),
            Validator.required(self.data_de_validade,"Data de validade"),
            Validator.date(self.data_de_validade,"Data de validade"),
            Validator.required(self.especificacao,"Especificação"),
            Validator.min_length(self.especificacao,"Especificação",5),
            Validator.required(self.unidade_medida,"Unidade de medida"),
        ]
        return [erro for erro in erros if erro]
    @classmethod
    def find_all(cls, order_by="id DESC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
            SELECT * FROM produto
            ORDER BY nome
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_nome(cls, nome):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT * FROM {cls.table} WHERE nome LIKE %s ORDER BY nome ASC
            """
            cursor.execute(sql, (f"%{nome}%",))
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
                "SELECT COUNT(*) FROM pedido_entrada WHERE produto_id = %s",
                "SELECT COUNT(*) FROM pedido_saida WHERE produto_id = %s",
                "SELECT COUNT(*) FROM item_entrada WHERE produto_id = %s",
                "SELECT COUNT(*) FROM item_saida WHERE produto_id = %s"
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
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            produto = cls.find_by_id(id)
            if not produto:
                raise ValueError("Produto não encontrado.")
            # Exclui todas as movimentações do produto
            cursor.execute("DELETE FROM movimentacao WHERE produto_id = %s",(id,))
            # Exclui o produto
            cursor.execute("DELETE FROM produto WHERE id = %s",(id,))
            conexao.commit()
            return True
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()
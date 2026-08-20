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
            Validator.required(self.data_de_validade, "Data de validade"),
            Validator.date(self.data_de_validade, "Data de validade"),
            Validator.required(self.especificacao, "Especificação"),
            Validator.min_length(self.especificacao, "Especificação", 5),
            Validator.required(self.unidade_medida, "Unidade de medida"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_all(cls, order_by="nome ASC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = f"""
                SELECT *
                FROM {cls.table}
                ORDER BY {order_by}
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_all_com_localizacao(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
                SELECT
                    p.*,
                    l.rua,
                    l.numero,
                    l.andar
                FROM produto p
                LEFT JOIN localizacao l
                    ON l.id = p.localizacao_id
                ORDER BY p.nome
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
                SELECT *
                FROM {cls.table}
                WHERE nome LIKE %s
                ORDER BY nome ASC
            """
            cursor.execute(sql, (f"%{nome}%",))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def aumentar_estoque(cls, produto_id, quantidade):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                UPDATE produto
                SET quantidade = quantidade + %s
                WHERE id = %s
            """
            cursor.execute(
                sql,
                (quantidade, produto_id)
            )
            conexao.commit()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def diminuir_estoque(cls, produto_id, quantidade):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                UPDATE produto
                SET quantidade = quantidade - %s
                WHERE id = %s
                AND quantidade >= %s
            """
            cursor.execute(
                sql,
                (
                    quantidade,
                    produto_id,
                    quantidade
                )
            )
            conexao.commit()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            queries = [
                "SELECT COUNT(*) FROM movimentacao WHERE pedido_entrada = %s",
                "SELECT COUNT(*) FROM movimentacao WHERE pedido_saida = %s",
                "SELECT COUNT(*) FROM movimentacao WHERE item_entrada = %s",
                "SELECT COUNT(*) FROM movimentacao WHERE item_saida = %s"
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
        produto = cls.find_by_id(id)
        if not produto:
            raise ValueError("Produto não encontrado.")
        if cls.has_related_records(id):
            raise ValueError(
                "Não é possível excluir o produto porque "
                "existem movimentações vinculadas."
            )
        return cls.delete(id)
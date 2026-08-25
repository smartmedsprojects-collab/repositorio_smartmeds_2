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
        "quantidade",
    ]

    def __init__(
        self,
        nome,
        marca,
        data_de_validade,
        especificacao,
        unidade_medida,
        quantidade=0
    ):
        self.nome = nome
        self.marca = marca
        self.data_de_validade = data_de_validade
        self.especificacao = especificacao
        self.unidade_medida = unidade_medida
        self.quantidade = int(quantidade)


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
            Validator.required(self.quantidade,"Quantidade"),
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
            cursor.execute(sql, (quantidade, produto_id))
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
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
                (quantidade, produto_id, quantidade)
            )
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()


    @classmethod
    def has_related_records(cls, produto_id):
        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
        # Verifica se existem movimentações vinculadas ao produto
            sql = """
                SELECT COUNT(*)
                FROM movimentacao
                WHERE produto_id = %s
            """

            cursor.execute(sql, (produto_id,))
            resultado = cursor.fetchone()

            return resultado[0] > 0

        finally:
            cursor.close()
            conexao.close()


    @classmethod
    def safe_delete(cls, produto_id):
        produto = cls.find_by_id(produto_id)

        if not produto:
            raise ValueError("Produto não encontrado.")

        if cls.has_related_records(produto_id):
            raise ValueError(
                "Não é possível excluir o produto porque "
                "existem movimentações vinculadas.")

        return cls.delete(produto_id)
    
    @classmethod
    def delete_movimentacoes(cls, produto_id):
        """
        Exclui todas as movimentações vinculadas ao produto.
        Retorna a quantidade de movimentações excluídas.
        """
        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
            sql = """
                DELETE FROM movimentacao
                WHERE produto_id = %s
            """

            cursor.execute(sql, (produto_id,))
            conexao.commit()

            return cursor.rowcount

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, produto_id):
        """
        Exclui primeiro as movimentações do produto
        e depois exclui o produto.
        """

        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
            # 1. Verifica se o produto existe
            sql_produto = """
                SELECT id
                FROM produto
                WHERE id = %s
            """

            cursor.execute(sql_produto, (produto_id,))
            produto = cursor.fetchone()

            if not produto:
                raise ValueError("Produto não encontrado.")

            # 2. Exclui as movimentações do produto
            sql_movimentacao = """
                DELETE FROM movimentacao
                WHERE produto_id = %s
            """

            cursor.execute(sql_movimentacao, (produto_id,))

            movimentacoes_excluidas = cursor.rowcount

            # 3. Exclui o produto
            sql_produto_delete = """
                DELETE FROM produto
                WHERE id = %s
            """

            cursor.execute(sql_produto_delete, (produto_id,))

            produto_excluido = cursor.rowcount

            # 4. Confirma tudo
            conexao.commit()

            return {
                "produto_excluido": produto_excluido,
                "movimentacoes_excluidas": movimentacoes_excluidas
            }

        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()
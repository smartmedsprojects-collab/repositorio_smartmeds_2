from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Produto(CrudBase):
    table = "produto"

<<<<<<< HEAD
    fields = [
        "nome",
        "marca",
        "data_de_validade",
        "especificacao",
        "unidade_medida",
        "quantidade",
        "usuario_id"
    ]

    def __init__(
        self,
        nome,
        marca,
        data_de_validade,
        especificacao,
        unidade_medida,
        usuario_id=None,
        quantidade=0
=======
    fields = ["nome", "marca", "data_de_validade", "especificacao", "unidade_medida"]

    def __init__(
        self, nome, marca, data_de_validade, especificacao, unidade_medida, quantidade=0
>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a
    ):
        self.nome = nome
        self.marca = marca
        self.data_de_validade = data_de_validade
        self.especificacao = especificacao
        self.unidade_medida = unidade_medida
        self.quantidade = int(quantidade)
        self.usuario_id = int(usuario_id) if usuario_id else None

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
            Validator.required(self.quantidade, "Quantidade"),
            Validator.required(self.usuario_id, "Usuário"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_all(cls, usuario_id=None, order_by="nome ASC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            if usuario_id is not None:
                sql = f"""
                    SELECT *
                    FROM {cls.table}
                    WHERE usuario_id = %s
                    ORDER BY {order_by}
                """
                cursor.execute(sql, (usuario_id,))
            else:
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
    def find_all_com_localizacao(cls, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            if usuario_id is not None:
                sql = """
                    SELECT
                        p.*,
                        l.rua,
                        l.numero,
                        l.andar
                    FROM produto p
                    LEFT JOIN localizacao l
                        ON l.id = p.localizacao_id
                    WHERE p.usuario_id = %s
                    ORDER BY p.nome
                """
                cursor.execute(sql, (usuario_id,))
            else:
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
    def find_by_nome(cls, nome, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            if usuario_id is not None:
                sql = f"""
                    SELECT *
                    FROM {cls.table}
                    WHERE nome LIKE %s AND usuario_id = %s
                    ORDER BY nome ASC
                """
                cursor.execute(sql, (f"%{nome}%", usuario_id))
            else:
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
<<<<<<< HEAD
=======
    def quantidade_em_estoque(cls, produto_id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                SELECT COALESCE(
                    SUM(
                        CASE
                            WHEN tipo_movimentacao IN ('SAIDA', 'SAÍDA')
                                THEN -quantidade
                            ELSE quantidade
                        END
                    ), 0
                )
                FROM movimentacao
                WHERE produto_id = %s
            """
            cursor.execute(sql, (produto_id,))
            return int(cursor.fetchone()[0] or 0)
        finally:
            cursor.close()
            conexao.close()


    @classmethod
>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a
    def aumentar_estoque(cls, produto_id, quantidade):
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

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
<<<<<<< HEAD
=======

            return cursor.lastrowid

>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a
        except Exception:
            conexao.rollback()
            raise

        finally:
            cursor.close()
            conexao.close()


    @classmethod
    def diminuir_estoque(cls, produto_id, quantidade):
<<<<<<< HEAD
=======
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")

        estoque = cls.quantidade_em_estoque(produto_id)

        if quantidade > estoque:
            return None

>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a
        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
            sql = """
                UPDATE produto
                SET quantidade = quantidade - %s
                WHERE id = %s
                AND quantidade >= %s
            """
<<<<<<< HEAD
            cursor.execute(sql, (quantidade, produto_id, quantidade))
=======

            cursor.execute(sql, (quantidade, produto_id))
>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a
            conexao.commit()

            return cursor.lastrowid

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
    def delete_movimentacoes(cls, produto_id):
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
<<<<<<< HEAD
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql_produto = """
                SELECT id
                FROM produto
                WHERE id = %s
            """
            cursor.execute(sql_produto, (produto_id,))
            produto = cursor.fetchone()

            if not produto:
                raise ValueError("Produto não encontrado.")

            sql_movimentacao = """
                DELETE FROM movimentacao
                WHERE produto_id = %s
            """
            cursor.execute(sql_movimentacao, (produto_id,))
            movimentacoes_excluidas = cursor.rowcount

            sql_produto_delete = """
                DELETE FROM produto
                WHERE id = %s
            """
            cursor.execute(sql_produto_delete, (produto_id,))
            produto_excluido = cursor.rowcount

            conexao.commit()

            return {
                "produto_excluido": produto_excluido,
                "movimentacoes_excluidas": movimentacoes_excluidas
            }
=======
        """
        Exclui definitivamente o produto e os registros dependentes.

        A ordem é importante por causa das chaves estrangeiras:
        1. item_entrada / item_saida
        2. movimentacao
        3. produto

        Tudo acontece na mesma transação para evitar exclusão parcial.
        """
        conexao = Database.connect()
        cursor = conexao.cursor()

        try:
            cursor.execute("SELECT id FROM produto WHERE id = %s", (produto_id,))
            if not cursor.fetchone():
                raise ValueError("Produto não encontrado.")

            cursor.execute(
                "SELECT id FROM movimentacao WHERE produto_id = %s", (produto_id,)
            )
            movimentacao_ids = [row[0] for row in cursor.fetchall()]

            if movimentacao_ids:
                placeholders = ", ".join(["%s"] * len(movimentacao_ids))

                cursor.execute(
                    f"DELETE FROM item_entrada WHERE movimentacao_id IN ({placeholders})",
                    tuple(movimentacao_ids),
                )

                cursor.execute(
                    f"DELETE FROM item_saida WHERE movimentacao_id IN ({placeholders})",
                    tuple(movimentacao_ids),
                )

                cursor.execute(
                    f"DELETE FROM movimentacao WHERE id IN ({placeholders})",
                    tuple(movimentacao_ids),
                )

            cursor.execute("DELETE FROM produto WHERE id = %s", (produto_id,))

            conexao.commit()
            return cursor.rowcount

>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
<<<<<<< HEAD
            conexao.close()
=======
            conexao.close()
>>>>>>> 1ccce1f834d440ff42c2a414893ad8a534ace11a

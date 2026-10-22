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
            cursor.execute(sql, (quantidade, produto_id, quantidade))
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
        """Exclui o produto e os registros dependentes em uma única transação.

        Os itens de entrada/saída que apontam para as movimentações do produto
        são removidos primeiro para respeitar as chaves estrangeiras. Os
        cabeçalhos dos pedidos são preservados.
        """
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            cursor.execute(
                "SELECT id FROM produto WHERE id = %s FOR UPDATE",
                (produto_id,),
            )
            produto = cursor.fetchone()
            if not produto:
                raise ValueError("Produto não encontrado.")

            # Bloqueia e identifica as movimentações vinculadas ao produto.
            cursor.execute(
                "SELECT id FROM movimentacao WHERE produto_id = %s FOR UPDATE",
                (produto_id,),
            )
            movimentacoes = cursor.fetchall()
            ids_movimentacao = [int(linha[0]) for linha in movimentacoes]

            itens_entrada_excluidos = 0
            itens_saida_excluidos = 0
            movimentacoes_excluidas = 0

            if ids_movimentacao:
                placeholders = ", ".join(["%s"] * len(ids_movimentacao))
                parametros = tuple(ids_movimentacao)

                # Primeiro exclui as linhas filhas; caso contrário, o MySQL
                # impede a exclusão da movimentação (FK item_entrada/item_saida).
                cursor.execute(
                    f"DELETE FROM item_entrada WHERE movimentacao_id IN ({placeholders})",
                    parametros,
                )
                itens_entrada_excluidos = cursor.rowcount

                cursor.execute(
                    f"DELETE FROM item_saida WHERE movimentacao_id IN ({placeholders})",
                    parametros,
                )
                itens_saida_excluidos = cursor.rowcount

                cursor.execute(
                    "DELETE FROM movimentacao WHERE produto_id = %s",
                    (produto_id,),
                )
                movimentacoes_excluidas = cursor.rowcount

            cursor.execute("DELETE FROM produto WHERE id = %s", (produto_id,))
            produto_excluido = cursor.rowcount
            if produto_excluido != 1:
                raise ValueError("O produto não foi excluído. Atualize a página e tente novamente.")

            conexao.commit()
            return {
                "produto_excluido": produto_excluido,
                "movimentacoes_excluidas": movimentacoes_excluidas,
                "itens_entrada_excluidos": itens_entrada_excluidos,
                "itens_saida_excluidos": itens_saida_excluidos,
            }
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

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
        self.numero_documento = (numero_documento or "").strip()
        self.fornecedor = (fornecedor or "").strip()
        self.data_entrada = data_entrada
        self.usuario_id = int(usuario_id) if usuario_id else None
        self.observacao = (observacao or "").strip()
        self.status = (status or "").strip()

    def validate(self):
        erros = [
            Validator.required(self.numero_documento, "Número do documento"),
            Validator.required(self.fornecedor, "Fornecedor"),
            Validator.required(self.data_entrada, "Data de entrada"),
            Validator.required(self.usuario_id, "Usuário"),
            Validator.required(self.status, "Status"),
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def _colunas_tabela(cls, cursor):
        """Retorna as colunas presentes na tabela para compatibilidade de esquemas."""
        cursor.execute(f"SHOW COLUMNS FROM `{cls.table}`")
        linhas = cursor.fetchall()
        return {
            linha.get("Field") if isinstance(linha, dict) else linha[0]
            for linha in linhas
        }

    @classmethod
    def _coluna_usuario(cls, cursor):
        colunas = cls._colunas_tabela(cursor)
        if "usuario_id" in colunas:
            return "usuario_id"
        if "id_usuario" in colunas:
            return "id_usuario"
        return None

    @classmethod
    def find_all(cls, usuario_id=None, order_by=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            coluna_usuario = cls._coluna_usuario(cursor)
            order_by = order_by or cls.pk
            # Os valores de order_by são definidos pelas rotas do próprio sistema.
            if usuario_id is not None and not coluna_usuario:
                raise RuntimeError(
                    "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                )

            if coluna_usuario:
                sql = f"""
                    SELECT pe.*, u.nome AS usuario
                    FROM `{cls.table}` pe
                    LEFT JOIN usuario u ON u.id = pe.`{coluna_usuario}`
                """
            else:
                sql = f"SELECT pe.* FROM `{cls.table}` pe"

            parametros = ()
            if usuario_id is not None:
                sql += f" WHERE pe.`{coluna_usuario}` = %s"
                parametros = (usuario_id,)
            sql += f" ORDER BY pe.`{order_by.replace(' DESC', '').replace(' ASC', '')}`"
            if order_by.upper().endswith(" DESC"):
                sql += " DESC"
            elif order_by.upper().endswith(" ASC"):
                sql += " ASC"

            cursor.execute(sql, parametros)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_id(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            coluna_usuario = cls._coluna_usuario(cursor)
            if coluna_usuario:
                sql = f"SELECT pe.*, pe.`{coluna_usuario}` AS usuario_id FROM `{cls.table}` pe WHERE pe.`{cls.pk}` = %s"
            else:
                sql = f"SELECT * FROM `{cls.table}` WHERE `{cls.pk}` = %s"
            parametros = [id]
            if usuario_id is not None:
                if not coluna_usuario:
                    raise RuntimeError(
                        "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                    )
                sql += f" AND `{coluna_usuario}` = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    def insert(self):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            coluna_usuario = self._coluna_usuario(cursor)
            if not coluna_usuario:
                raise RuntimeError(
                    "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                )
            colunas = [coluna_usuario if campo == "usuario_id" else campo for campo in self.fields]
            valores = tuple(getattr(self, campo) for campo in self.fields)
            sql = (
                f"INSERT INTO `{self.table}` ({', '.join(f'`{c}`' for c in colunas)}) "
                f"VALUES ({', '.join(['%s'] * len(colunas))})"
            )
            cursor.execute(sql, valores)
            conexao.commit()
            return cursor.lastrowid
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    def update(self, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            coluna_usuario = self._coluna_usuario(cursor)
            if not coluna_usuario:
                raise RuntimeError(
                    "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                )
            colunas = [coluna_usuario if campo == "usuario_id" else campo for campo in self.fields]
            campos_sql = ", ".join(f"`{campo}` = %s" for campo in colunas)
            valores = list(getattr(self, campo) for campo in self.fields)
            sql = f"UPDATE `{self.table}` SET {campos_sql} WHERE `{self.pk}` = %s"
            valores.append(id)
            if usuario_id is not None:
                sql += f" AND `{coluna_usuario}` = %s"
                valores.append(usuario_id)
            cursor.execute(sql, tuple(valores))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def delete(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            coluna_usuario = cls._coluna_usuario(cursor)
            sql = f"DELETE FROM `{cls.table}` WHERE `{cls.pk}` = %s"
            parametros = [id]
            if usuario_id is not None:
                if not coluna_usuario:
                    raise RuntimeError(
                        "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                    )
                sql += f" AND `{coluna_usuario}` = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def listar_movimentacoes(cls, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            coluna_usuario = cls._coluna_usuario(cursor)
            if not coluna_usuario:
                raise RuntimeError(
                    "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                )
            sql = f"""
                SELECT
                    pe.id_pedido_entrada,
                    pe.numero_documento,
                    pe.fornecedor,
                    pe.data_entrada,
                    pe.observacao,
                    pe.status,
                    u.nome AS usuario
                FROM `{cls.table}` pe
                LEFT JOIN usuario u ON u.id = pe.`{coluna_usuario}`
                WHERE pe.`{coluna_usuario}` = %s
                ORDER BY pe.data_entrada DESC
            """
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM item_entrada WHERE pedido_entrada_id = %s",
                (id,),
            )
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id, usuario_id=None):
        """Exclui o pedido e seus itens em transação, revertendo entradas reais do estoque."""
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            conexao.start_transaction()
            coluna_usuario = cls._coluna_usuario(cursor)

            sql_pedido = f"SELECT * FROM `{cls.table}` WHERE `{cls.pk}` = %s"
            parametros_pedido = [id]
            if usuario_id is not None:
                if not coluna_usuario:
                    raise RuntimeError(
                        "A tabela pedido_entrada não possui coluna de usuário reconhecida."
                    )
                sql_pedido += f" AND `{coluna_usuario}` = %s"
                parametros_pedido.append(usuario_id)
            sql_pedido += " FOR UPDATE"
            cursor.execute(sql_pedido, tuple(parametros_pedido))
            pedido = cursor.fetchone()
            if not pedido:
                raise ValueError("Pedido de entrada não encontrado ou acesso negado.")

            cursor.execute(
                """
                SELECT
                    ie.id AS item_id,
                    ie.quantidade,
                    ie.movimentacao_id,
                    m.produto_id,
                    UPPER(COALESCE(m.tipo_movimentacao, '')) AS tipo_movimentacao
                FROM item_entrada ie
                LEFT JOIN movimentacao m ON m.id = ie.movimentacao_id
                WHERE ie.pedido_entrada_id = %s
                FOR UPDATE
                """,
                (id,),
            )
            itens = cursor.fetchall()

            # Só revertemos estoque para movimentos identificados como ENTRADA.
            # Registros antigos ligados a movimentos CADASTRO não representam uma
            # entrada comprovada e não devem reduzir o saldo por engano.
            quantidades_para_reverter = {}
            ids_movimentacao_entrada = set()
            for item in itens:
                tipo = (item.get("tipo_movimentacao") or "").strip().upper()
                produto_id = item.get("produto_id")
                quantidade = int(item.get("quantidade") or 0)
                movimentacao_id = item.get("movimentacao_id")
                if tipo == "ENTRADA" and produto_id is not None and quantidade > 0:
                    quantidades_para_reverter[produto_id] = (
                        quantidades_para_reverter.get(produto_id, 0) + quantidade
                    )
                    if movimentacao_id is not None:
                        ids_movimentacao_entrada.add(movimentacao_id)

            for produto_id, quantidade in quantidades_para_reverter.items():
                cursor.execute(
                    "SELECT quantidade FROM produto WHERE id = %s FOR UPDATE",
                    (produto_id,),
                )
                produto = cursor.fetchone()
                if not produto:
                    raise ValueError(
                        "Não é possível excluir o pedido: um produto vinculado não foi encontrado."
                    )
                estoque_atual = int(produto.get("quantidade") or 0)
                if estoque_atual < quantidade:
                    raise ValueError(
                        "Não é possível excluir este pedido porque o estoque atual de um dos "
                        "produtos é menor que a quantidade que precisa ser revertida. "
                        "Confira as saídas realizadas antes de excluir."
                    )
                cursor.execute(
                    "UPDATE produto SET quantidade = quantidade - %s WHERE id = %s AND quantidade >= %s",
                    (quantidade, produto_id, quantidade),
                )
                if cursor.rowcount != 1:
                    raise RuntimeError(
                        "O estoque foi alterado durante a exclusão. Tente novamente."
                    )

            # Primeiro removemos os itens para respeitar a chave estrangeira.
            cursor.execute(
                "DELETE FROM item_entrada WHERE pedido_entrada_id = %s", (id,)
            )

            # Remove movimentos ENTRADA que ficaram sem itens associados. Movimentos
            # usados por outros pedidos/saídas e os registros de CADASTRO são preservados.
            for movimentacao_id in ids_movimentacao_entrada:
                cursor.execute(
                    """
                    SELECT
                        (SELECT COUNT(*) FROM item_entrada WHERE movimentacao_id = %s) AS entradas,
                        (SELECT COUNT(*) FROM item_saida WHERE movimentacao_id = %s) AS saidas
                    """,
                    (movimentacao_id, movimentacao_id),
                )
                referencias = cursor.fetchone() or {}
                if int(referencias.get("entradas") or 0) == 0 and int(referencias.get("saidas") or 0) == 0:
                    cursor.execute(
                        "DELETE FROM movimentacao WHERE id = %s AND UPPER(COALESCE(tipo_movimentacao, '')) = 'ENTRADA'",
                        (movimentacao_id,),
                    )

            sql_excluir = f"DELETE FROM `{cls.table}` WHERE `{cls.pk}` = %s"
            parametros_excluir = [id]
            if usuario_id is not None:
                sql_excluir += f" AND `{coluna_usuario}` = %s"
                parametros_excluir.append(usuario_id)
            cursor.execute(sql_excluir, tuple(parametros_excluir))
            if cursor.rowcount != 1:
                raise ValueError("O pedido não foi excluído; confira o acesso ao registro.")

            conexao.commit()
            return True
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

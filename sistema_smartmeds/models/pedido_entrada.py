import re

from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class PedidoEntrada(CrudBase):
    table = "pedido_entrada"
    pk = "id_pedido_entrada"
    user_fk = "id_usuario"

    fields = [
        "numero_documento",
        "fornecedor",
        "data_entrada",
        "id_usuario",
        "observacao",
        "status",
    ]

    def __init__(
        self,
        numero_documento="",
        fornecedor="",
        data_entrada=None,
        usuario_id=None,
        observacao="",
        status="ABERTO",
        id_usuario=None,
        **kwargs,
    ):
        self.numero_documento = (numero_documento or "").strip()
        self.fornecedor = (fornecedor or "").strip()
        self.data_entrada = data_entrada
        responsavel = id_usuario if id_usuario not in (None, "", 0, "0") else usuario_id
        self.id_usuario = int(responsavel) if responsavel not in (None, "", 0, "0") else None
        self.observacao = (observacao or "").strip()
        self.status = (status or "ABERTO").strip().upper()

    def validate(self):
        erros = [
            Validator.required(self.numero_documento, "Número do documento"),
            Validator.required(self.fornecedor, "Fornecedor"),
            Validator.required(self.data_entrada, "Data de entrada"),
            Validator.date(self.data_entrada, "Data de entrada"),
            Validator.required(self.id_usuario, "Usuário"),
            Validator.required(self.status, "Status"),
        ]
        if self.status and self.status not in {"ABERTO", "PENDENTE", "FINALIZADO", "CANCELADO"}:
            erros.append("O status do pedido de entrada é inválido.")
        return [erro for erro in erros if erro]

    @classmethod
    def coluna_usuario(cls, cursor):
        """Retorna a coluna proprietária existente no banco legado ou atual.

        Algumas instalações antigas usam ``usuario_id``; o esquema atual usa
        ``id_usuario``. A escolha é feita a partir do próprio banco, sem alterar
        dados e sem remover o filtro por usuário.
        """
        cursor.execute(
            """SELECT COLUMN_NAME
               FROM information_schema.columns
               WHERE table_schema = DATABASE() AND table_name = %s""",
            (cls.table,),
        )
        linhas = cursor.fetchall()
        colunas = set()
        for linha in linhas:
            if isinstance(linha, dict):
                nome = linha.get("COLUMN_NAME") or linha.get("column_name")
                if nome is None and linha:
                    nome = next(iter(linha.values()))
            else:
                nome = linha[0] if linha else None
            if nome:
                colunas.add(str(nome))

        if "id_usuario" in colunas:
            return "id_usuario"
        if "usuario_id" in colunas:
            return "usuario_id"
        raise RuntimeError(
            "A tabela pedido_entrada não possui a coluna de proprietário "
            "'id_usuario' nem 'usuario_id'. Faça backup e ajuste o esquema do "
            "banco antes de usar os pedidos de entrada."
        )

    @classmethod
    def _select_com_usuario(cls, cursor, condicao="", parametros=(), order_by=None):
        coluna = cls.coluna_usuario(cursor)
        alias_usuario = "" if coluna == "id_usuario" else f", pe.{coluna} AS id_usuario"
        sql = f"SELECT pe.*{alias_usuario} FROM {cls.table} pe"
        if condicao:
            sql += f" WHERE {condicao}"
        if order_by:
            permitido = re.fullmatch(
                r"(id_pedido_entrada|numero_documento|fornecedor|data_entrada|status|criado_em)(?:\s+(ASC|DESC))?",
                order_by.strip(),
                flags=re.IGNORECASE,
            )
            if not permitido:
                raise ValueError("Campo de ordenação inválido para pedidos de entrada.")
            sql += " ORDER BY " + permitido.group(1)
            if permitido.group(2):
                sql += " " + permitido.group(2).upper()
        cursor.execute(sql, tuple(parametros))
        return cursor.fetchall()

    @classmethod
    def find_all(cls, usuario_id=None, order_by=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            coluna = cls.coluna_usuario(cursor)
            condicao = f"pe.{coluna} = %s" if usuario_id is not None else ""
            parametros = (usuario_id,) if usuario_id is not None else ()
            return cls._select_com_usuario(
                cursor, condicao=condicao, parametros=parametros,
                order_by=order_by or "id_pedido_entrada DESC",
            )
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_id(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            coluna = cls.coluna_usuario(cursor)
            condicao = "pe.id_pedido_entrada = %s"
            parametros = [id]
            if usuario_id is not None:
                condicao += f" AND pe.{coluna} = %s"
                parametros.append(usuario_id)
            registros = cls._select_com_usuario(cursor, condicao, tuple(parametros))
            return registros[0] if registros else None
        finally:
            cursor.close()
            conexao.close()

    def insert(self):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            coluna_usuario = self.coluna_usuario(cursor)
            colunas = [coluna_usuario if campo == "id_usuario" else campo for campo in self.fields]
            nomes = ", ".join(colunas)
            marcadores = ", ".join(["%s"] * len(colunas))
            valores = tuple(getattr(self, campo) for campo in self.fields)
            cursor.execute(
                f"INSERT INTO {self.table} ({nomes}) VALUES ({marcadores})",
                valores,
            )
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
            coluna_usuario = self.coluna_usuario(cursor)
            colunas = [coluna_usuario if campo == "id_usuario" else campo for campo in self.fields]
            campos = ", ".join(f"{campo} = %s" for campo in colunas)
            valores = list(getattr(self, campo) for campo in self.fields) + [id]
            sql = f"UPDATE {self.table} SET {campos} WHERE {self.pk} = %s"
            if usuario_id is not None:
                sql += f" AND {coluna_usuario} = %s"
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
    def listar_movimentacoes(cls, usuario_id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            coluna = cls.coluna_usuario(cursor)
            sql = f"""
                SELECT pe.id_pedido_entrada, pe.numero_documento,
                       pe.fornecedor, pe.data_entrada, pe.observacao,
                       pe.status, pe.{coluna} AS id_usuario,
                       u.nome AS usuario
                FROM pedido_entrada pe
                LEFT JOIN usuario u ON pe.{coluna} = u.id
                WHERE pe.{coluna} = %s
                ORDER BY pe.data_entrada DESC, pe.id_pedido_entrada DESC
            """
            cursor.execute(sql, (usuario_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            coluna_usuario = cls.coluna_usuario(cursor)
            sql = "SELECT id_pedido_entrada FROM pedido_entrada WHERE id_pedido_entrada = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += f" AND {coluna_usuario} = %s"
                parametros.append(usuario_id)
            sql += " FOR UPDATE"
            cursor.execute(sql, tuple(parametros))
            if not cursor.fetchone():
                raise ValueError("Pedido de entrada não encontrado ou acesso negado.")

            cursor.execute("SELECT COUNT(*) FROM item_entrada WHERE pedido_entrada_id = %s", (id,))
            if cursor.fetchone()[0]:
                raise ValueError(
                    "Não é possível excluir este pedido porque existem itens de entrada vinculados."
                )

            sql = "DELETE FROM pedido_entrada WHERE id_pedido_entrada = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += f" AND {coluna_usuario} = %s"
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

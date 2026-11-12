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
        "precisa_temperatura_baixa",
        "usuario_id",
    ]

    def __init__(
        self,
        nome="",
        marca="",
        data_de_validade=None,
        especificacao="",
        unidade_medida="Unidade",
        usuario_id=None,
        quantidade=0,
        id=None,
        precisa_temperatura_baixa=0,
    ):
        self.id = id
        self.nome = (nome or "").strip()
        self.marca = (marca or "").strip()
        self.data_de_validade = data_de_validade
        self.especificacao = (especificacao or "").strip()
        self.unidade_medida = (unidade_medida or "Unidade").strip()
        try:
            self.quantidade = int(quantidade) if quantidade not in (None, "") else 0
        except (TypeError, ValueError):
            self.quantidade = -1
        self.usuario_id = int(usuario_id) if usuario_id not in (None, "", 0, "0") else None
        try:
            self.precisa_temperatura_baixa = (
                int(precisa_temperatura_baixa)
                if precisa_temperatura_baixa not in (None, "")
                else 0
            )
        except (TypeError, ValueError):
            self.precisa_temperatura_baixa = -1

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
            Validator.non_negative(self.quantidade, "Quantidade"),
            Validator.required(self.usuario_id, "Usuário"),
        ]
        if self.precisa_temperatura_baixa not in (0, 1):
            erros.append("Informe se o produto precisa de refrigeração.")
        return [erro for erro in erros if erro]

    @classmethod
    def find_all(cls, usuario_id=None, order_by="nome ASC"):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            if usuario_id is not None:
                sql = f"SELECT * FROM {cls.table} WHERE usuario_id = %s ORDER BY {order_by}"
                cursor.execute(sql, (usuario_id,))
            else:
                sql = f"SELECT * FROM {cls.table} ORDER BY {order_by}"
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
            sql = """
                SELECT p.*, l.rua, l.numero, l.andar
                FROM produto p
                LEFT JOIN localizacao l
                  ON l.id = p.localizacao_id AND l.usuario_id = p.usuario_id
            """
            parametros = ()
            if usuario_id is not None:
                sql += " WHERE p.usuario_id = %s"
                parametros = (usuario_id,)
            sql += " ORDER BY p.nome"
            cursor.execute(sql, parametros)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_nome(cls, nome, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM produto WHERE nome LIKE %s"
            parametros = [f"%{nome}%"]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            sql += " ORDER BY nome ASC"
            cursor.execute(sql, tuple(parametros))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def aumentar_estoque(cls, produto_id, quantidade, usuario_id=None):
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = "UPDATE produto SET quantidade = quantidade + %s WHERE id = %s"
            parametros = [quantidade, produto_id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            if cursor.rowcount != 1:
                raise ValueError("Produto não encontrado ou acesso negado.")
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def diminuir_estoque(cls, produto_id, quantidade, usuario_id=None):
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = """
                UPDATE produto SET quantidade = quantidade - %s
                WHERE id = %s AND quantidade >= %s
            """
            parametros = [quantidade, produto_id, quantidade]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            if cursor.rowcount != 1:
                raise ValueError("Estoque insuficiente ou produto não encontrado.")
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
            cursor.execute("SELECT COUNT(*) FROM movimentacao WHERE produto_id = %s", (produto_id,))
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def delete_movimentacoes(cls, produto_id):
        """Remove apenas movimentações que não tenham itens de entrada/saída vinculados."""
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            cursor.execute(
                """SELECT COUNT(*) FROM movimentacao m
                   WHERE m.produto_id = %s AND (
                     EXISTS (SELECT 1 FROM item_entrada i WHERE i.movimentacao_id = m.id)
                     OR EXISTS (SELECT 1 FROM item_saida s WHERE s.movimentacao_id = m.id)
                   )""",
                (produto_id,),
            )
            if cursor.fetchone()[0]:
                raise ValueError("Existem itens vinculados ao histórico deste produto.")
            cursor.execute("DELETE FROM movimentacao WHERE produto_id = %s", (produto_id,))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, produto_id, usuario_id=None):
        """Exclui o produto somente quando isso não apaga histórico de entrada/saída."""
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = "SELECT id FROM produto WHERE id = %s"
            parametros = [produto_id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            sql += " FOR UPDATE"
            cursor.execute(sql, tuple(parametros))
            if not cursor.fetchone():
                raise ValueError("Produto não encontrado ou acesso negado.")

            cursor.execute(
                """SELECT COUNT(*) FROM movimentacao m
                   WHERE m.produto_id = %s AND (
                     EXISTS (SELECT 1 FROM item_entrada i WHERE i.movimentacao_id = m.id)
                     OR EXISTS (SELECT 1 FROM item_saida s WHERE s.movimentacao_id = m.id)
                   )""",
                (produto_id,),
            )
            if cursor.fetchone()[0]:
                raise ValueError(
                    "Este produto possui itens de entrada/saída vinculados ao histórico. "
                    "Para preservar os registros de estoque, não é possível excluí-lo."
                )

            cursor.execute("DELETE FROM movimentacao WHERE produto_id = %s", (produto_id,))
            sql = "DELETE FROM produto WHERE id = %s"
            parametros = [produto_id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            if cursor.rowcount != 1:
                raise ValueError("Produto não encontrado ou acesso negado.")
            conexao.commit()
            return {"produto_excluido": 1}
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

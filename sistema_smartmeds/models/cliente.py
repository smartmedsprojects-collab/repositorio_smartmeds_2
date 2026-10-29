from core.crud_base import CrudBase
from core.database import Database
from core.security import gerar_hash_senha
from core.validator import Validator


class Cliente(CrudBase):
    table = "cliente"
    fields = ["nome", "email", "senha", "cnpj", "usuario_id"]

    def __init__(self, nome="", email="", senha="", cnpj="", usuario_id=None, id=None):
        self.id = id
        self.nome = (nome or "").strip()
        self.email = (email or "").strip().lower()
        self.senha = (senha or "").strip()
        self.cnpj = "".join(filter(str.isdigit, str(cnpj or "")))
        self.usuario_id = int(usuario_id) if usuario_id not in (None, "", 0, "0") else None

    def validate(self, exigir_senha=True):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.required(self.email, "E-mail"),
            Validator.email(self.email),
            Validator.required(self.cnpj, "CNPJ"),
            Validator.cnpj(self.cnpj),
            Validator.required(self.usuario_id, "Usuário"),
        ]
        if exigir_senha or self.senha:
            erros.extend([
                Validator.required(self.senha, "Senha"),
                Validator.min_length(self.senha, "Senha", 8),
            ])
            if len(self.senha.encode("utf-8")) > 72:
                erros.append("A senha deve ter no máximo 72 bytes em UTF-8.")
        return [erro for erro in erros if erro]

    def insert(self):
        self.senha = gerar_hash_senha(self.senha)
        return super().insert()

    def update(self, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql_busca = "SELECT senha FROM cliente WHERE id = %s"
            parametros = [id]
            if usuario_id is not None:
                sql_busca += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql_busca, tuple(parametros))
            atual = cursor.fetchone()
            if not atual:
                raise ValueError("Cliente não encontrado ou acesso negado.")

            senha_hash = gerar_hash_senha(self.senha) if self.senha else atual["senha"]
            sql = """
                UPDATE cliente
                SET nome = %s, email = %s, senha = %s, cnpj = %s
                WHERE id = %s
            """
            valores = [self.nome, self.email, senha_hash, self.cnpj, id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
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
    def safe_delete(cls, id, usuario_id=None):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            sql = "SELECT id FROM cliente WHERE id = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
                parametros.append(usuario_id)
            cursor.execute(sql, tuple(parametros))
            if not cursor.fetchone():
                raise ValueError("Cliente não encontrado ou acesso negado.")

            cursor.execute("SELECT COUNT(*) FROM pedido_saida WHERE cliente_id = %s", (id,))
            if cursor.fetchone()[0]:
                raise ValueError(
                    "Não é possível excluir este cliente porque existem pedidos de saída vinculados."
                )

            sql = "DELETE FROM cliente WHERE id = %s"
            parametros = [id]
            if usuario_id is not None:
                sql += " AND usuario_id = %s"
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

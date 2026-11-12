from core.crud_base import CrudBase
from core.database import Database
from core.security import verificar_senha, gerar_hash_senha
from core.validator import Validator


class Usuario(CrudBase):
    table = "usuario"
    fields = ["nome", "email", "senha", "tipo", "identificacao"]

    def __init__(self, nome="", email="", senha="", tipo="", identificacao=""):
        self.nome = (nome or "").strip()
        self.email = (email or "").strip().lower()
        self.senha = (senha or "").strip()
        self.tipo = (tipo or "").strip().lower()
        self.identificacao = (identificacao or "").strip()

    def validate(self, exigir_senha=True):
        erros = [
            Validator.required(self.nome, "Nome"),
            Validator.min_length(self.nome, "Nome", 3),
            Validator.required(self.email, "E-mail"),
            Validator.email(self.email),
            Validator.required(self.tipo, "Tipo de usuário"),
            Validator.required(self.identificacao, "Identificação"),
        ]
        if self.tipo and self.tipo not in {"adm", "admin", "estoquista", "consulta"}:
            erros.append("O tipo de usuário é inválido.")
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

    def update(self, id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute("SELECT senha FROM usuario WHERE id = %s", (id,))
            usuario_atual = cursor.fetchone()
            if not usuario_atual:
                raise ValueError("Usuário não encontrado.")

            senha_hash = gerar_hash_senha(self.senha) if self.senha else usuario_atual["senha"]
            cursor.execute(
                """UPDATE usuario
                   SET nome = %s, email = %s, senha = %s, tipo = %s, identificacao = %s
                   WHERE id = %s""",
                (self.nome, self.email, senha_hash, self.tipo, self.identificacao, id),
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
    def validar_no_banco(cls, email, senha=None, identificacao=None):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT id, nome, email, senha, tipo, identificacao
                   FROM usuario WHERE email = %s""",
                ((email or "").strip().lower(),),
            )
            usuario = cursor.fetchone()
            if not usuario:
                return {"valido": False, "mensagem": "E-mail ou usuário não encontrado.", "usuario": None}

            if senha is not None and not verificar_senha(senha, usuario["senha"]):
                return {"valido": False, "mensagem": "Senha incorreta.", "usuario": None}

            if identificacao is not None and str(identificacao).strip() != str(usuario["identificacao"]).strip():
                return {"valido": False, "mensagem": "Identificação não corresponde ao usuário.", "usuario": None}

            return {"valido": True, "mensagem": "Dados validados com sucesso.", "usuario": usuario}
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def autenticar(cls, email, senha):
        resultado = cls.validar_no_banco(email=email, senha=senha)
        return resultado["usuario"] if resultado["valido"] else None

    @classmethod
    def safe_delete(cls, id):
        """Impede remover um usuário que ainda seja dono de dados do sistema."""
        conexao = Database.connect()
        cursor = conexao.cursor()
        tabelas = (
            ("cliente", "usuario_id"),
            ("localizacao", "usuario_id"),
            ("produto", "usuario_id"),
            ("pedido_entrada", "id_usuario"),
            ("pedido_saida", "usuario_id"),
            ("fornecedor", "usuario_id"),
        )
        try:
            cursor.execute("SELECT id FROM usuario WHERE id = %s FOR UPDATE", (id,))
            if not cursor.fetchone():
                raise ValueError("Usuário não encontrado.")

            for tabela, coluna in tabelas:
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_schema = DATABASE() AND table_name = %s",
                    (tabela,),
                )
                if not cursor.fetchone()[0]:
                    continue
                if tabela == "pedido_entrada":
                    from models.pedido_entrada import PedidoEntrada
                    coluna = PedidoEntrada.coluna_usuario(cursor)
                cursor.execute(
                    f"SELECT COUNT(*) FROM {tabela} WHERE {coluna} = %s",
                    (id,),
                )
                if cursor.fetchone()[0]:
                    raise ValueError(
                        "Não é possível excluir este usuário porque ele possui registros vinculados. "
                        "Transfira ou arquive os dados antes de tentar novamente."
                    )

            cursor.execute("DELETE FROM usuario WHERE id = %s", (id,))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()


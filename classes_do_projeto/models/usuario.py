from core.crud_base import CrudBase
from core.database import Database
from core.security import verificar_senha, gerar_hash_senha


class Usuario(CrudBase):

    table = "usuario"

    fields = [
        "nome",
        "email",
        "senha",
        "tipo",
        "identificacao"
    ]

    def __init__(
        self,
        nome,
        email,
        senha,
        tipo,
        identificacao
    ):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tipo = tipo
        self.identificacao = identificacao

    def insert(self):
        """
        Cria um novo usuário.
        A senha é transformada em hash antes de ser salva.
        """

        self.senha = gerar_hash_senha(self.senha)

        return super().insert()

    @classmethod
    def validar_no_banco(
        cls,
        email,
        senha=None,
        identificacao=None
    ):

        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)

        try:

            sql = """
                SELECT id, nome, email, senha, tipo, identificacao
                FROM usuario
                WHERE email = %s
            """

            cursor.execute(sql, (email,))

            usuario = cursor.fetchone()

            # Usuário não encontrado

            if not usuario:
                return {
                    "valido": False,
                    "mensagem": "E-mail ou usuário não encontrado.",
                    "usuario": None
                }

            # Validação da senha

            if senha is not None:

                if not verificar_senha(
                    senha,
                    usuario["senha"]
                ):
                    return {
                        "valido": False,
                        "mensagem": "Senha incorreta.",
                        "usuario": None
                    }

            # Validação da identificação

            if identificacao is not None:

                if str(identificacao).strip() != str(
                    usuario["identificacao"]
                ).strip():

                    return {
                        "valido": False,
                        "mensagem": "Identificação não corresponde ao usuário.",
                        "usuario": None
                    }

            return {
                "valido": True,
                "mensagem": "Dados validados com sucesso.",
                "usuario": usuario
            }

        finally:

            cursor.close()
            conexao.close()

    @classmethod
    def autenticar(cls, email, senha):

        resultado = cls.validar_no_banco(
            email=email,
            senha=senha
        )

        if resultado["valido"]:
            return resultado["usuario"]

        return None
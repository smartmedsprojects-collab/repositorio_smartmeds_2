from core.database import fetch_one, execute
from core.security import hash_senha, verificar_senha


class Usuario:
    @staticmethod
    def autenticar(email, senha):
        usuario = fetch_one("SELECT id, nome, email, senha_hash FROM usuarios WHERE email = %s", (email,))
        if usuario and verificar_senha(usuario["senha_hash"], senha):
            usuario.pop("senha_hash", None)
            return usuario
        return None

    @staticmethod
    def criar(nome, email, senha):
        return execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (%s, %s, %s)",
            (nome, email, hash_senha(senha)),
        )[0]

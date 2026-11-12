from functools import wraps

from flask import session, redirect, url_for, flash

import bcrypt


def gerar_hash_senha(senha):
    if not isinstance(senha, str) or not senha:
        raise ValueError("Informe uma senha válida.")
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > 72:
        raise ValueError("A senha deve ter no máximo 72 bytes em UTF-8.")
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha_digitada, senha_hash_banco):
    try:
        if not isinstance(senha_digitada, str) or not isinstance(senha_hash_banco, str):
            return False
        senha_bytes = senha_digitada.encode("utf-8")
        if len(senha_bytes) > 72:
            return False
        return bcrypt.checkpw(senha_bytes, senha_hash_banco.encode("utf-8"))
    except (ValueError, TypeError, AttributeError):
        # Senhas legadas em texto puro ou hashes inválidos não devem derrubar o login.
        return False


def login_obrigatorio(funcao):
    

    @wraps(funcao)
    def wrapper(*args, **kwargs):

        if "usuario_id" not in session:
            flash(
                "Faça login para acessar o sistema.",
                "warning"
            )

            return redirect(url_for("login"))

        return funcao(*args, **kwargs)

    return wrapper
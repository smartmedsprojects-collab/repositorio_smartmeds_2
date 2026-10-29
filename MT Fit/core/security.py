"""Hash de senha e criptografia reversível do CPF."""
from cryptography.fernet import Fernet, InvalidToken
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash


def hash_senha(senha):
    return generate_password_hash(senha, method="scrypt")


def verificar_senha(senha_hash, senha):
    return bool(senha_hash) and check_password_hash(senha_hash, senha)


def _fernet():
    key = current_app.config.get("CPF_ENCRYPTION_KEY")
    if not key:
        raise RuntimeError(
            "Configure CPF_ENCRYPTION_KEY no ambiente. Gere uma chave com: "
            "python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
        )
    try:
        return Fernet(key.encode() if isinstance(key, str) else key)
    except Exception as exc:
        raise RuntimeError("CPF_ENCRYPTION_KEY inválida; use uma chave Fernet válida.") from exc


def criptografar_cpf(cpf):
    digitos = ''.join(ch for ch in str(cpf) if ch.isdigit())
    if len(digitos) != 11:
        raise ValueError("O CPF deve conter 11 números.")
    return _fernet().encrypt(digitos.encode()).decode()


def descriptografar_cpf(valor):
    try:
        return _fernet().decrypt(valor.encode()).decode()
    except (InvalidToken, ValueError, TypeError):
        return ""


def mascarar_cpf(valor):
    cpf = descriptografar_cpf(valor)
    return f"***.***.***-{cpf[9:]}" if len(cpf) == 11 else "CPF indisponível"

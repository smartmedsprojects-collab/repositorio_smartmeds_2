from getpass import getpass

from models.usuario import Usuario


def main():
    print("=== Cadastro inicial de administrador SmartMeds ===")
    nome = input("Nome completo: ").strip()
    email = input("E-mail: ").strip().lower()
    identificacao = input("Identificação: ").strip()
    senha = getpass("Senha (mínimo 8 caracteres): ")
    confirmar = getpass("Confirme a senha: ")

    if senha != confirmar:
        raise SystemExit("Erro: as senhas não correspondem.")

    usuario = Usuario(
        nome=nome,
        email=email,
        senha=senha,
        tipo="adm",
        identificacao=identificacao,
    )
    erros = usuario.validate()
    if erros:
        raise SystemExit("\n".join(erros))

    try:
        usuario.insert()
    except Exception as erro:
        raise SystemExit(
            "Não foi possível cadastrar o administrador. Verifique se o banco está configurado "
            "e se o e-mail/identificação já existem."
        ) from erro

    print("Administrador cadastrado com sucesso.")


if __name__ == "__main__":
    main()

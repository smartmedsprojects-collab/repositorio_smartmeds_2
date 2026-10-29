# FitManager — Sistema de gerenciamento de academia

Aplicação web em Python + Flask + SQLite, com cadastro de alunos, planos de treinamento, agendamentos e login.

## Requisitos
- Python 3.10 ou superior
- pip

## Instalação no Windows
Abra o terminal dentro da pasta do projeto e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Se o PowerShell bloquear a ativação, execute diretamente:
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Abra `http://127.0.0.1:5000`.

## Login de demonstração
- E-mail: `admin@academia.com`
- Senha: `Academia@123`

Também são criadas as contas `recepcao@academia.com` / `Recepcao@123` e `gestor@academia.com` / `Gestor@123`.

**Troque as senhas de demonstração antes de usar com dados reais.** O sistema cria `academia.db` e `cpf.key` automaticamente. Faça backup seguro da chave `cpf.key`: sem ela, os CPFs criptografados existentes não poderão ser recuperados. Não envie essa chave ao Git nem a terceiros.

## Recursos
- Login com validação e sessão expirada após 30 minutos de inatividade.
- Proteção CSRF nos formulários.
- CPF criptografado em repouso com Fernet; a listagem exibe CPF mascarado.
- Cadastro, pesquisa e edição de alunos.
- Cadastro de planos associados a alunos já cadastrados.
- Cadastro de agendamentos e atualização da data/hora.
- Agendamentos ordenados por data/hora.
- Painel com indicadores e próximos agendamentos.

## Segurança e LGPD
Este é um projeto acadêmico inicial, não uma certificação de conformidade com a LGPD. Antes de produção: configure `FLASK_SECRET_KEY` e `CPF_ENCRYPTION_KEY` em um gerenciador de segredos, ative HTTPS e `COOKIE_SECURE=1`, substitua senhas de demonstração, defina controles de acesso, política de retenção, backup e processo de atendimento aos titulares. O arquivo `cpf.key` é gerado localmente se `CPF_ENCRYPTION_KEY` não estiver configurada.

Para gerar uma chave de CPF manualmente:
```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Defina o valor gerado na variável `CPF_ENCRYPTION_KEY` antes de iniciar o sistema pela primeira vez.

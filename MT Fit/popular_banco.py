"""Adiciona dados demonstrativos sem apagar dados existentes.
Execute somente após configurar MySQL e CPF_ENCRYPTION_KEY.
"""
from datetime import date, timedelta
from app import app
from core.database import fetch_all, fetch_one, execute
from core.security import criptografar_cpf, hash_senha

USUARIOS = [
    ("Administrador Demonstração", "admin.demo@academia.com", "Demo@12345"),
    ("Recepção Demonstração", "recepcao.demo@academia.com", "Demo@12345"),
    ("Gestor Demonstração", "gestor.demo@academia.com", "Demo@12345"),
]
ALUNOS = [
    ("Ana Martins", "529.982.247-25", "ana.demo@exemplo.com", "11987654321"),
    ("Bruno Costa", "111.444.777-35", "bruno.demo@exemplo.com", "11987654322"),
    ("Carla Souza", "935.411.347-80", "carla.demo@exemplo.com", "11987654323"),
]
PLANOS = [
    ("Treino A — corpo inteiro", "Condicionamento"),
    ("Treino B — força", "Força"),
    ("Treino C — resistência", "Resistência"),
]


def main():
    with app.app_context():
        # Adiciona contas de demonstração sem duplicar e-mails.
        for nome, email, senha in USUARIOS:
            if not fetch_one("SELECT id FROM usuarios WHERE email=%s", (email,)):
                execute("INSERT INTO usuarios (nome,email,senha_hash) VALUES (%s,%s,%s)",
                        (nome, email, hash_senha(senha)))

        # Garante ao menos três alunos no total; não altera registros existentes.
        for nome, cpf, email, telefone in ALUNOS:
            if not fetch_one("SELECT id FROM alunos WHERE email=%s", (email,)):
                total = fetch_one("SELECT COUNT(*) AS total FROM alunos")["total"]
                if total < 3:
                    execute("INSERT INTO alunos (nome,cpf_criptografado,email,telefone) VALUES (%s,%s,%s,%s)",
                            (nome, criptografar_cpf(cpf), email, telefone))

        alunos = fetch_all("SELECT id FROM alunos ORDER BY id LIMIT 3")
        if len(alunos) < 1:
            raise RuntimeError("Cadastre pelo menos um aluno antes de popular planos.")

        # Garante pelo menos três planos e usa alunos já existentes.
        total_planos = fetch_one("SELECT COUNT(*) AS total FROM planos")["total"]
        for idx, (descricao, objetivo) in enumerate(PLANOS):
            if total_planos >= 3:
                break
            aluno_id = alunos[idx % len(alunos)]["id"]
            execute("INSERT INTO planos (descricao,objetivo,alunos_id) VALUES (%s,%s,%s)",
                    (descricao, objetivo, aluno_id))
            total_planos += 1

        planos = fetch_all("SELECT id FROM planos ORDER BY id LIMIT 3")
        if len(planos) < 1:
            raise RuntimeError("Não foi possível criar planos para popular agendamentos.")

        total_ag = fetch_one("SELECT COUNT(*) AS total FROM agendamentos")["total"]
        for idx in range(total_ag, 3):
            plano_id = planos[idx % len(planos)]["id"]
            dia = date.today() + timedelta(days=idx + 1)
            hora = ["09:00:00", "14:00:00", "18:30:00"][idx]
            execute("INSERT INTO agendamentos (data,horario,observacao,planos_id) VALUES (%s,%s,%s,%s)",
                    (dia.isoformat(), hora, f"Sessão demonstrativa {idx + 1}", plano_id))

        print("Popularização concluída. Verifique os dados antes de usar em ambiente real.")
        print("Contas demo adicionadas (se não existiam): admin.demo@academia.com, recepcao.demo@academia.com, gestor.demo@academia.com")
        print("Senha das contas demo: Demo@12345")


if __name__ == "__main__":
    main()

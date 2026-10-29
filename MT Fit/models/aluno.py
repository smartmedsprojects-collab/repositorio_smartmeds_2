from core.database import fetch_all, fetch_one, execute
from core.security import criptografar_cpf, mascarar_cpf


class Aluno:
    @staticmethod
    def listar(busca=""):
        termo = f"%{busca.strip()}%"
        rows = fetch_all(
            "SELECT id, nome, cpf_criptografado, email, telefone FROM alunos "
            "WHERE nome LIKE %s OR email LIKE %s ORDER BY nome",
            (termo, termo),
        )
        for row in rows:
            row["cpf_mascarado"] = mascarar_cpf(row["cpf_criptografado"])
        return rows

    @staticmethod
    def buscar(aluno_id):
        return fetch_one("SELECT * FROM alunos WHERE id = %s", (aluno_id,))

    @staticmethod
    def criar(nome, cpf, email, telefone):
        return execute(
            "INSERT INTO alunos (nome, cpf_criptografado, email, telefone) VALUES (%s, %s, %s, %s)",
            (nome, criptografar_cpf(cpf), email, telefone),
        )[0]

    @staticmethod
    def atualizar(aluno_id, nome, cpf, email, telefone):
        return execute(
            "UPDATE alunos SET nome=%s, cpf_criptografado=%s, email=%s, telefone=%s WHERE id=%s",
            (nome, criptografar_cpf(cpf), email, telefone, aluno_id),
        )[1]

    @staticmethod
    def excluir(aluno_id):
        return execute("DELETE FROM alunos WHERE id=%s", (aluno_id,))[1]

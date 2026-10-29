from core.database import fetch_all, fetch_one, execute


class Plano:
    @staticmethod
    def listar():
        return fetch_all(
            "SELECT p.id, p.descricao, p.objetivo, p.alunos_id, a.nome AS aluno_nome "
            "FROM planos p JOIN alunos a ON a.id=p.alunos_id ORDER BY a.nome, p.descricao"
        )

    @staticmethod
    def buscar(plano_id):
        return fetch_one("SELECT * FROM planos WHERE id=%s", (plano_id,))

    @staticmethod
    def criar(descricao, objetivo, aluno_id):
        return execute(
            "INSERT INTO planos (descricao, objetivo, alunos_id) VALUES (%s, %s, %s)",
            (descricao, objetivo or None, aluno_id),
        )[0]

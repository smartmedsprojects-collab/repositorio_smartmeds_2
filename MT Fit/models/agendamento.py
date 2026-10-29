from core.database import fetch_all, fetch_one, execute


class Agendamento:
    @staticmethod
    def listar():
        return fetch_all(
            "SELECT ag.id, ag.data, ag.horario, ag.observacao, ag.planos_id, "
            "p.descricao AS plano_descricao, p.objetivo, a.id AS aluno_id, a.nome AS aluno_nome "
            "FROM agendamentos ag JOIN planos p ON p.id=ag.planos_id "
            "JOIN alunos a ON a.id=p.alunos_id "
            "ORDER BY ag.data, ag.horario"
        )

    @staticmethod
    def buscar(agendamento_id):
        return fetch_one("SELECT * FROM agendamentos WHERE id=%s", (agendamento_id,))

    @staticmethod
    def criar(data, horario, observacao, plano_id):
        return execute(
            "INSERT INTO agendamentos (data, horario, observacao, planos_id) VALUES (%s, %s, %s, %s)",
            (data, horario, observacao, plano_id),
        )[0]

    @staticmethod
    def atualizar(agendamento_id, data, horario, observacao, plano_id):
        return execute(
            "UPDATE agendamentos SET data=%s, horario=%s, observacao=%s, planos_id=%s WHERE id=%s",
            (data, horario, observacao, plano_id, agendamento_id),
        )[1]

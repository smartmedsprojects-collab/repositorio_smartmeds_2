from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

class Localizacao(CrudBase):
    table = "localizacao"
    fields = [
        "nome",
        "descricao",
        "setor",
        "corredor",
        "prateleira"
    ]

    def __init__(self, nome, descricao, setor, corredor, prateleira):
        self.nome = nome
        self.descricao = descricao
        self.setor = setor
        self.corredor = corredor
        self.prateleira = prateleira
    def validate(self):
        erros = [
            Validator.required(self.nome, "nome"),
            Validator.required(self.setor, "setor"),
            Validator.required(self.corredor, "corredor"),
            Validator.required(self.prateleira, "prateleira")
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def find_by_setor(cls, setor):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = "SELECT * FROM localizacao WHERE setor = %s ORDER BY nome"
            cursor.execute(sql, (setor,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            queries = [
                "SELECT COUNT(*) FROM produto WHERE localizacao_id = %s",
                "SELECT COUNT(*) FROM movimentacao WHERE localizacao_id = %s"
            ]
            total = 0
            for sql in queries:
                cursor.execute(sql, (id,))
                total += cursor.fetchone()[0]
            return total > 0
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def safe_delete(cls, id):
        localizacao = cls.find_by_id(id)
        if not localizacao:
            raise ValueError("Localização não encontrada.")
        if cls.has_related_records(id):
            raise ValueError("Não é possível excluir a localização porque ela possui registros vinculados.")
        cls.delete(id)
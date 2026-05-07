from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator

class Fornecedor(CrudBase):
    table = "fornecedor"
    fields = [
        "nome",
        "cnpj",
        "telefone",
        "email",
        "endereco"
    ]

    def __init__(self, nome, cnpj, telefone, email, endereco):
        self.nome = nome
        self.cnpj = cnpj
        self.telefone = telefone
        self.email = email
        self.endereco = endereco

    def validate(self):
        
        erros = [
            Validator.required(self.nome, "nome"),
            Validator.required(self.cnpj, "cnpj"),
            Validator.required(self.telefone, "telefone"),
            Validator.required(self.email, "email"),
            Validator.required(self.endereco, "endereço")
        ]
        return [erro for erro in erros if erro]

    @classmethod
    def has_related_records(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            queries = [
                "SELECT COUNT(*) FROM produto WHERE fornecedor_id = %s",
                "SELECT COUNT(*) FROM pedido WHERE fornecedor_id = %s"
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
        fornecedor = cls.find_by_id(id)
        if not fornecedor:
            raise ValueError("Fornecedor não encontrado.")
        if cls.has_related_records(id):
            raise ValueError("Não é possível excluir o fornecedor porque ele possui registros vinculados.")
        cls.delete(id)


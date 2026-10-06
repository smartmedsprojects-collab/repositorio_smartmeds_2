from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator


class Cliente(CrudBase):

    table = "cliente"

    
    fields = [
        "nome",
        "email",
        "senha",
        "cnpj",
        "usuario_id"
    ]

    def __init__(
        self,
        nome,
        email,
        senha,
        cnpj,
        usuario_id,
        id=None  
    ):
        self.id = id  
        self.nome = nome.strip() if nome else ""
        self.email = email.strip().lower() if email else ""
        self.senha = senha.strip() if senha else ""
        self.cnpj = cnpj.strip() if cnpj else ""
        self.usuario_id = int(usuario_id) if usuario_id else None
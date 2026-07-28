from models.usuario import Usuario
from core.security import gerar_hash_senha

usuario = Usuario(
    nome="mecanico admin",
    email="davi.r.ribeiro8@aluno.senai.br",
    senha=gerar_hash_senha("123456"),
    tipo="admin",
    identificacao="0001"
)

usuario.insert()

print("Administrador criado com sucesso")
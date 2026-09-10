from models.usuario import Usuario
from core.security import gerar_hash_senha

usuario = Usuario(
    nome="Davi admin",
    email="admin@smartmeds.com",
    senha=gerar_hash_senha("123456"),
    tipo="admin",
    identificacao="001010"
)

usuario.insert()

print("Administrador criado com sucesso")
-- Execute no MySQL Workbench sobre o banco Academia_db EXISTENTE.
-- Faça backup antes de executar. Não apaga tabelas nem registros.
USE `Academia_db`;

-- Werkzeug scrypt/pbkdf2 hashes ocupam mais que 45 caracteres.
ALTER TABLE `usuarios`
  MODIFY COLUMN `nome` VARCHAR(100) NOT NULL,
  MODIFY COLUMN `email` VARCHAR(150) NOT NULL,
  MODIFY COLUMN `senha_hash` VARCHAR(255) NOT NULL;

-- Fernet gera tokens maiores que 45 caracteres para um CPF.
ALTER TABLE `alunos`
  MODIFY COLUMN `nome` VARCHAR(100) NOT NULL,
  MODIFY COLUMN `cpf_criptografado` VARCHAR(255) NOT NULL,
  MODIFY COLUMN `email` VARCHAR(150) NOT NULL,
  MODIFY COLUMN `telefone` VARCHAR(20) NOT NULL;

-- Para evitar duplicidade de CPF criptografado não se cria UNIQUE aqui: Fernet
-- usa nonce aleatório e o mesmo CPF gera tokens diferentes. Valide duplicidade
-- antes de criptografar se essa regra for necessária.

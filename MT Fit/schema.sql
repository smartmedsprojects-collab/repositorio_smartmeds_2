-- Estrutura de referência compatível com os models deste projeto.
-- Se Academia_db já existe, NÃO execute CREATE TABLE às cegas; use migrations.sql.
CREATE SCHEMA IF NOT EXISTS `Academia_db` DEFAULT CHARACTER SET utf8mb4;
USE `Academia_db`;

CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(150) NOT NULL,
  `senha_hash` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`), UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `alunos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `cpf_criptografado` VARCHAR(255) NOT NULL,
  `email` VARCHAR(150) NOT NULL,
  `telefone` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`), UNIQUE KEY `email_UNIQUE` (`email`)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `planos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `descricao` VARCHAR(100) NOT NULL,
  `objetivo` VARCHAR(50) NULL,
  `alunos_id` INT NOT NULL,
  PRIMARY KEY (`id`), KEY `fk_planos_alunos1_idx` (`alunos_id`),
  CONSTRAINT `fk_planos_alunos1` FOREIGN KEY (`alunos_id`) REFERENCES `alunos` (`id`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS `agendamentos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `data` DATE NOT NULL,
  `horario` TIME NOT NULL,
  `observacao` VARCHAR(100) NOT NULL,
  `planos_id` INT NOT NULL,
  PRIMARY KEY (`id`), KEY `fk_agendamentos_planos_idx` (`planos_id`),
  CONSTRAINT `fk_agendamentos_planos` FOREIGN KEY (`planos_id`) REFERENCES `planos` (`id`)
    ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB;

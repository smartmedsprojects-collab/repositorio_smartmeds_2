-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
SHOW WARNINGS;
-- -----------------------------------------------------
-- Schema smartmeds
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema smartmeds
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS smartmeds DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
SHOW WARNINGS;
USE smartmeds ;

-- -----------------------------------------------------
-- Table cliente
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cliente (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  senha VARCHAR(255) NOT NULL,
  cnpj VARCHAR(14) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE INDEX email (email ASC) VISIBLE,
  UNIQUE INDEX cnpj (cnpj ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table localizacao
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS localizacao (
  id INT NOT NULL AUTO_INCREMENT,
  rua VARCHAR(100) NOT NULL,
  numero VARCHAR(10) NOT NULL,
  andar VARCHAR(10) NULL DEFAULT NULL,
  PRIMARY KEY (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table usuario
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS usuario (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  datas VARCHAR(100) NOT NULL,
  tipo VARCHAR(10) NOT NULL,
  identificaçâo VARCHAR(13) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE INDEX datas (datas ASC) VISIBLE,
  UNIQUE INDEX tipo (tipo ASC) VISIBLE,
  UNIQUE INDEX identificaçâo (identificaçâo ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table produto
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS produto (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  marca VARCHAR(100) NULL DEFAULT NULL,
  data_de_validade DATE NULL DEFAULT NULL,
  especificacao TEXT NULL DEFAULT NULL,
  unidade_medida VARCHAR(50) NULL DEFAULT NULL,
  localizacao_id INT NULL DEFAULT NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_produto_localizacao (localizacao_id ASC) VISIBLE,
  INDEX fk_produto_usuario1_idx (usuario_id ASC) VISIBLE,
  CONSTRAINT fk_produto_localizacao
    FOREIGN KEY (localizacao_id)
    REFERENCES localizacao (id),
  CONSTRAINT fk_produto_usuario1
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table estoque
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS estoque (
  id INT NOT NULL AUTO_INCREMENT,
  tipo_movimentacao VARCHAR(50) NULL DEFAULT NULL,
  data_movimentacao DATE NULL DEFAULT NULL,
  quantidade INT NOT NULL,
  quantidade_min INT NULL DEFAULT NULL,
  produto_id INT NULL DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX fk_estoque_produto (produto_id ASC) VISIBLE,
  CONSTRAINT fk_estoque_produto
    FOREIGN KEY (produto_id)
    REFERENCES produto (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table fornecedor
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS fornecedor (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  senha VARCHAR(255) NOT NULL,
  cnpj VARCHAR(18) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE INDEX email (email ASC) VISIBLE,
  UNIQUE INDEX cnpj (cnpj ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table pedido_entrada
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido_entrada (
  id INT NOT NULL AUTO_INCREMENT,
  tipo VARCHAR(50) NULL DEFAULT NULL,
  pagamento VARCHAR(50) NULL DEFAULT NULL,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  data_pagamento DATE NULL DEFAULT NULL,
  fornecedor_id INT NULL DEFAULT NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_pedido_entrada_fornecedor (fornecedor_id ASC) VISIBLE,
  INDEX fk_pedido_entrada_usuario1_idx (usuario_id ASC) VISIBLE,
  CONSTRAINT fk_pedido_entrada_fornecedor
    FOREIGN KEY (fornecedor_id)
    REFERENCES fornecedor (id),
  CONSTRAINT fk_pedido_entrada_usuario1
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table item_entrada
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS item_entrada (
  id INT NOT NULL AUTO_INCREMENT,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  pedido_entrada_id INT NULL DEFAULT NULL,
  estoque_id INT NULL DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX fk_item_entrada_pedido (pedido_entrada_id ASC) VISIBLE,
  INDEX fk_item_entrada_estoque (estoque_id ASC) VISIBLE,
  CONSTRAINT fk_item_entrada_estoque
    FOREIGN KEY (estoque_id)
    REFERENCES estoque (id),
  CONSTRAINT fk_item_entrada_pedido
    FOREIGN KEY (pedido_entrada_id)
    REFERENCES pedido_entrada (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table pedido_saida
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido_saida (
  id INT NOT NULL AUTO_INCREMENT,
  tipo VARCHAR(50) NULL DEFAULT NULL,
  pagamento VARCHAR(50) NULL DEFAULT NULL,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  data_pagamento DATE NULL DEFAULT NULL,
  cliente_id INT NULL DEFAULT NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_pedido_saida_cliente (cliente_id ASC) VISIBLE,
  INDEX fk_pedido_saida_usuario1_idx (usuario_id ASC) VISIBLE,
  CONSTRAINT fk_pedido_saida_cliente
    FOREIGN KEY (cliente_id)
    REFERENCES cliente (id),
  CONSTRAINT fk_pedido_saida_usuario1
    FOREIGN KEY (usuario_id)
    REFERENCES usuario (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table item_saida
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS item_saida (
  id INT NOT NULL AUTO_INCREMENT,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  pedido_saida_id INT NULL DEFAULT NULL,
  estoque_id INT NULL DEFAULT NULL,
  PRIMARY KEY (id),
  INDEX fk_item_saida_pedido (pedido_saida_id ASC) VISIBLE,
  INDEX fk_item_saida_estoque (estoque_id ASC) VISIBLE,
  CONSTRAINT fk_item_saida_estoque
    FOREIGN KEY (estoque_id)
    REFERENCES estoque (id),
  CONSTRAINT fk_item_saida_pedido
    FOREIGN KEY (pedido_saida_id)
    REFERENCES pedido_saida (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
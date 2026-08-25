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
CREATE SCHEMA IF NOT EXISTS `smartmeds` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
SHOW WARNINGS;
USE `smartmeds` ;

-- -----------------------------------------------------
-- Table `cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliente` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `cnpj` VARCHAR(14) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE,
  UNIQUE INDEX `cnpj` (`cnpj` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `localizacao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `localizacao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `rua` VARCHAR(100) NOT NULL,
  `numero` VARCHAR(10) NOT NULL,
  `andar` VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `produto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `produto` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `marca` VARCHAR(100) NULL DEFAULT NULL,
  `data_de_validade` DATE NULL DEFAULT NULL,
  `especificacao` TEXT NULL DEFAULT NULL,
  `unidade_medida` VARCHAR(50) NULL DEFAULT NULL,
  `localizacao_id` INT NULL DEFAULT NULL,
  `quantidade` INT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  INDEX `fk_produto_localizacao` (`localizacao_id` ASC) VISIBLE,
  CONSTRAINT `fk_produto_localizacao`
    FOREIGN KEY (`localizacao_id`)
    REFERENCES `localizacao` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `movimentacao`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `movimentacao` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tipo_movimentacao` VARCHAR(50) NULL DEFAULT NULL,
  `data_movimentacao` DATETIME NULL DEFAULT NULL,
  `quantidade` INT NOT NULL,
  `quantidade_min` INT NULL DEFAULT NULL,
  `produto_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_movimentacao_produto` (`produto_id` ASC) VISIBLE,
  CONSTRAINT `fk_movimentacao_produto`
    FOREIGN KEY (`produto_id`)
    REFERENCES `produto` (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `usuario` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `senha` VARCHAR(255) NOT NULL,
  `tipo` VARCHAR(20) NOT NULL,
  `identificacao` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `pedido_entrada`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido_entrada` (
  `id_pedido_entrada` INT NOT NULL AUTO_INCREMENT,
  `numero_documento` VARCHAR(50) NULL DEFAULT NULL,
  `fornecedor` VARCHAR(100) NULL DEFAULT NULL,
  `data_entrada` DATE NOT NULL,
  `id_usuario` INT NOT NULL,
  `observacao` TEXT NULL DEFAULT NULL,
  `status` VARCHAR(30) NULL DEFAULT 'aberto',
  `criado_em` DATETIME NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pedido_entrada`),
  INDEX `fk_pedido_entrada_usuario` (`id_usuario` ASC) VISIBLE,
  CONSTRAINT `fk_pedido_entrada_usuario`
    FOREIGN KEY (`id_usuario`)
    REFERENCES `usuario` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `item_entrada`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `item_entrada` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quantidade` INT NOT NULL,
  `valor` DECIMAL(10,2) NULL DEFAULT NULL,
  `pedido_entrada_id` INT NULL DEFAULT NULL,
  `movimentacao_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_item_entrada_pedido` (`pedido_entrada_id` ASC) VISIBLE,
  INDEX `fk_item_entrada_movimentacao` (`movimentacao_id` ASC) VISIBLE,
  CONSTRAINT `fk_item_entrada_movimentacao`
    FOREIGN KEY (`movimentacao_id`)
    REFERENCES `movimentacao` (`id`),
  CONSTRAINT `fk_item_entrada_pedido`
    FOREIGN KEY (`pedido_entrada_id`)
    REFERENCES `pedido_entrada` (`id_pedido_entrada`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `pedido_saida`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pedido_saida` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `tipo` VARCHAR(50) NULL DEFAULT NULL,
  `pagamento` VARCHAR(50) NULL DEFAULT NULL,
  `quantidade` INT NOT NULL,
  `valor` DECIMAL(10,2) NULL DEFAULT NULL,
  `data_pagamento` DATE NULL DEFAULT NULL,
  `cliente_id` INT NULL DEFAULT NULL,
  `usuario_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_pedido_saida_cliente` (`cliente_id` ASC) VISIBLE,
  INDEX `fk_pedido_saida_usuario` (`usuario_id` ASC) VISIBLE,
  CONSTRAINT `fk_pedido_saida_cliente`
    FOREIGN KEY (`cliente_id`)
    REFERENCES `cliente` (`id`),
  CONSTRAINT `fk_pedido_saida_usuario`
    FOREIGN KEY (`usuario_id`)
    REFERENCES `usuario` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table `item_saida`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `item_saida` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `quantidade` INT NOT NULL,
  `valor` DECIMAL(10,2) NULL DEFAULT NULL,
  `pedido_saida_id` INT NULL DEFAULT NULL,
  `movimentacao_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_item_saida_pedido` (`pedido_saida_id` ASC) VISIBLE,
  INDEX `fk_item_saida_movimentacao` (`movimentacao_id` ASC) VISIBLE,
  CONSTRAINT `fk_item_saida_movimentacao`
    FOREIGN KEY (`movimentacao_id`)
    REFERENCES `movimentacao` (`id`),
  CONSTRAINT `fk_item_saida_pedido`
    FOREIGN KEY (`pedido_saida_id`)
    REFERENCES `pedido_saida` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;

SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

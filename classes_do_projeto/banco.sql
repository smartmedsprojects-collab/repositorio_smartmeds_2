-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';


-- -----------------------------------------------------
-- Schema smartmeds
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS smartmeds DEFAULT CHARACTER SET utf8mb3 ;
SHOW WARNINGS;
USE smartmeds ;



-- -----------------------------------------------------
-- Table cliente
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS cliente (  -- ok --
  id INT NOT NULL,
  nome VARCHAR(45) NULL DEFAULT NULL,
  email VARCHAR(50) NULL DEFAULT NULL,
  telefone VARCHAR(15) NULL DEFAULT NULL,
  endereço VARCHAR(100) NULL DEFAULT NULL,
  cnpj VARCHAR(14) NULL DEFAULT NULL,
  PRIMARY KEY (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;



-- -----------------------------------------------------
-- Table localizacao
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS localizacao ( -- ok --
  id INT NOT NULL,
  rua VARCHAR(45) NULL DEFAULT NULL,
  numero DECIMAL(10,2) NULL DEFAULT NULL,
  andar DECIMAL(10,2) NULL DEFAULT NULL,
  PRIMARY KEY (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;



-- -----------------------------------------------------
-- Table produto
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS produto ( -- ok --
  id INT NOT NULL,
  nome VARCHAR(45) NULL DEFAULT NULL,
  marca VARCHAR(45) NULL DEFAULT NULL,
  data_de_validade VARCHAR(45) NULL DEFAULT NULL,
  especificação VARCHAR(45) NULL DEFAULT NULL,
  unidade_medida VARCHAR(20),
  localizacao_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_produto_localizacao1_idx (localizacao_id ASC) VISIBLE,
  CONSTRAINT fk_produto_localizacao1
    FOREIGN KEY (localizacao_id)
    REFERENCES localizacao (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table estoque
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS estoque ( -- ok --
  id INT NOT NULL,
  tipo_movimentacao VARCHAR(10) NOT NULL,
  data_movimentacao DATETIME NOT NULL,
  quantidade VARCHAR(45) NULL DEFAULT NULL,
  quantidade_min VARCHAR(45) NULL DEFAULT NULL,
  produto_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_estoque_produto1_idx (produto_id ASC) VISIBLE,
  CONSTRAINT fk_estoque_produto1
    FOREIGN KEY (produto_id)
    REFERENCES produto (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table fornecedor
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS fornecedor ( -- ok --
  id INT NOT NULL,
  nome VARCHAR(45) NOT NULL,
  email VARCHAR(50) NULL DEFAULT NULL,
  telefone VARCHAR(15) NULL DEFAULT NULL,
  endereço VARCHAR(100) NULL DEFAULT NULL,
  cnpj VARCHAR(14) NULL DEFAULT NULL,
  PRIMARY KEY (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table pedido entrada
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido_entrada ( -- ok --
  id INT NOT NULL,
  tipo VARCHAR(45) NULL DEFAULT NULL,
  pagamento DECIMAL(10,2) NULL DEFAULT NULL,
  quantidade VARCHAR(45) NULL DEFAULT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  data_pagamento TIMESTAMP NULL DEFAULT NULL,
  fornecedor_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_pedido_entrada_fornecedor_idx (fornecedor_id ASC) VISIBLE,
  CONSTRAINT fk_pedido_entrada_fornecedor
    FOREIGN KEY (fornecedor_id)
    REFERENCES fornecedor (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table item entrada
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS item_entrada ( -- ok --
  id INT NOT NULL,
  quantidade VARCHAR(45) NULL DEFAULT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  pedido_entrada_id INT NOT NULL,
  estoque_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_item_entrada_pedido_entrada1_idx (pedido_entrada_id ASC) VISIBLE,
  INDEX fk_item_entrada_estoque1_idx (estoque_id ASC) VISIBLE,
  CONSTRAINT fk_item_entrada_pedido_entrada1
    FOREIGN KEY (pedido_entrada_id)
    REFERENCES pedido_entrada (id),
  CONSTRAINT fk_item_entrada_estoque1
    FOREIGN KEY (estoque_id)
    REFERENCES estoque (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table pedido saida
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS pedido_saida ( -- ok --
  id INT NOT NULL,
  tipo VARCHAR(45) NULL DEFAULT NULL,
  pagamento DECIMAL(10,2) NULL DEFAULT NULL,
  quantidade VARCHAR(45) NULL DEFAULT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  data_pagamento TIMESTAMP NULL DEFAULT NULL,
  cliente_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_Pedido_saida_cliente1_idx (cliente_id ASC) VISIBLE,
  CONSTRAINT fk_Pedido_saida_cliente1
    FOREIGN KEY (cliente_id)
    REFERENCES cliente (id))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;

SHOW WARNINGS;

-- -----------------------------------------------------
-- Table item saida
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS item_saida ( -- ok --
  id INT NOT NULL,
  quantidade VARCHAR(45) NULL DEFAULT NULL,
  valor DECIMAL(10,2) NULL DEFAULT NULL,
  Pedido_saida_id INT NOT NULL,
  estoque_id INT NOT NULL,
  PRIMARY KEY (id),
  INDEX fk_item_saida_Pedido_saida1_idx (Pedido_saida_id ASC) VISIBLE,
  INDEX fk_item_saida_estoque1_idx (estoque_id ASC) VISIBLE,
  CONSTRAINT fk_item_saida_Pedido_saida1
    FOREIGN KEY (Pedido_saida_id)
    REFERENCES pedido_saida (id),
  CONSTRAINT fk_item_saida_estoque1
    FOREIGN KEY (estoque_id)
    REFERENCES estoque (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb3;


SHOW WARNINGS;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
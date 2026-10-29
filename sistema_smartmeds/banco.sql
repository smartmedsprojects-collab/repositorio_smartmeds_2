-- Schema inicial do SmartMeds (MySQL 8+).
-- Este arquivo contém somente estrutura; não apaga tabelas nem inclui dados pessoais.
-- Se a conexão usar outro banco, ajuste SMARTMEDS_DB_NAME em config.py e o USE abaixo.

CREATE DATABASE IF NOT EXISTS smartmeds3
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;
USE smartmeds3;

CREATE TABLE IF NOT EXISTS usuario (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  senha VARCHAR(255) NOT NULL,
  tipo VARCHAR(20) NOT NULL,
  identificacao VARCHAR(20) NOT NULL,
  permissao TINYINT NOT NULL DEFAULT 0,
  foto_nome VARCHAR(255) NULL,
  foto_caminho VARCHAR(500) NULL,
  foto_blob BLOB NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_usuario_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS cliente (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  senha VARCHAR(255) NOT NULL,
  cnpj VARCHAR(14) NOT NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_cliente_email (email),
  UNIQUE KEY uq_cliente_cnpj (cnpj),
  KEY idx_cliente_usuario (usuario_id),
  CONSTRAINT fk_cliente_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS localizacao (
  id INT NOT NULL AUTO_INCREMENT,
  rua VARCHAR(100) NOT NULL,
  numero VARCHAR(10) NOT NULL,
  andar VARCHAR(20) NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_localizacao_usuario (usuario_id),
  CONSTRAINT fk_localizacao_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS produto (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  marca VARCHAR(100) NULL,
  data_de_validade DATE NULL,
  especificacao TEXT NULL,
  unidade_medida VARCHAR(50) NULL,
  localizacao_id INT NULL,
  quantidade INT NOT NULL DEFAULT 0,
  precisa_temperatura_baixa TINYINT(1) NOT NULL DEFAULT 0,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_produto_localizacao (localizacao_id),
  KEY idx_produto_usuario (usuario_id),
  CONSTRAINT fk_produto_localizacao FOREIGN KEY (localizacao_id) REFERENCES localizacao (id),
  CONSTRAINT fk_produto_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id),
  CONSTRAINT chk_produto_quantidade CHECK (quantidade >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS movimentacao (
  id INT NOT NULL AUTO_INCREMENT,
  tipo_movimentacao VARCHAR(50) NULL,
  data_movimentacao DATETIME NULL,
  quantidade INT NOT NULL,
  quantidade_min INT NULL,
  produto_id INT NULL,
  PRIMARY KEY (id),
  KEY idx_movimentacao_produto (produto_id),
  KEY idx_movimentacao_data (data_movimentacao),
  CONSTRAINT fk_movimentacao_produto FOREIGN KEY (produto_id) REFERENCES produto (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sensor_leitura (
  id INT NOT NULL AUTO_INCREMENT,
  device_id VARCHAR(50) NOT NULL,
  sensor VARCHAR(30) NOT NULL DEFAULT 'DHT11',
  temperatura FLOAT NULL,
  umidade FLOAT NULL,
  -- Colunas antigas mantidas só para compatibilidade com bancos já existentes.
  distancia FLOAT NULL,
  rfid_uid VARCHAR(50) NULL,
  produto VARCHAR(100) NULL,
  movimento VARCHAR(30) NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_sensor_timestamp (sensor, timestamp),
  KEY idx_device_timestamp (device_id, timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS pedido_entrada (
  id_pedido_entrada INT NOT NULL AUTO_INCREMENT,
  numero_documento VARCHAR(50) NULL,
  fornecedor VARCHAR(100) NULL,
  data_entrada DATE NOT NULL,
  id_usuario INT NOT NULL,
  observacao TEXT NULL,
  status VARCHAR(30) NOT NULL DEFAULT 'ABERTO',
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_pedido_entrada),
  KEY idx_pedido_entrada_usuario (id_usuario),
  CONSTRAINT fk_pedido_entrada_usuario FOREIGN KEY (id_usuario) REFERENCES usuario (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS item_entrada (
  id INT NOT NULL AUTO_INCREMENT,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NOT NULL DEFAULT 0,
  pedido_entrada_id INT NOT NULL,
  movimentacao_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_item_entrada_pedido (pedido_entrada_id),
  KEY idx_item_entrada_movimentacao (movimentacao_id),
  CONSTRAINT fk_item_entrada_pedido FOREIGN KEY (pedido_entrada_id) REFERENCES pedido_entrada (id_pedido_entrada),
  CONSTRAINT fk_item_entrada_movimentacao FOREIGN KEY (movimentacao_id) REFERENCES movimentacao (id),
  CONSTRAINT chk_item_entrada_quantidade CHECK (quantidade >= 50),
  CONSTRAINT chk_item_entrada_valor CHECK (valor >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS pedido_saida (
  id INT NOT NULL AUTO_INCREMENT,
  tipo VARCHAR(50) NOT NULL,
  pagamento VARCHAR(50) NOT NULL,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NOT NULL DEFAULT 0,
  data_pagamento DATE NOT NULL,
  cliente_id INT NOT NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_pedido_saida_cliente (cliente_id),
  KEY idx_pedido_saida_usuario (usuario_id),
  CONSTRAINT fk_pedido_saida_cliente FOREIGN KEY (cliente_id) REFERENCES cliente (id),
  CONSTRAINT fk_pedido_saida_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id),
  CONSTRAINT chk_pedido_saida_quantidade CHECK (quantidade > 0),
  CONSTRAINT chk_pedido_saida_valor CHECK (valor >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS item_saida (
  id INT NOT NULL AUTO_INCREMENT,
  quantidade INT NOT NULL,
  valor DECIMAL(10,2) NOT NULL DEFAULT 0,
  pedido_saida_id INT NOT NULL,
  movimentacao_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_item_saida_pedido (pedido_saida_id),
  KEY idx_item_saida_movimentacao (movimentacao_id),
  CONSTRAINT fk_item_saida_pedido FOREIGN KEY (pedido_saida_id) REFERENCES pedido_saida (id),
  CONSTRAINT fk_item_saida_movimentacao FOREIGN KEY (movimentacao_id) REFERENCES movimentacao (id),
  CONSTRAINT chk_item_saida_quantidade CHECK (quantidade > 0),
  CONSTRAINT chk_item_saida_valor CHECK (valor >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Mantida para compatibilidade com o modelo Fornecedor, mesmo que o formulário
-- de pedido de entrada continue aceitando o nome do fornecedor como texto.
CREATE TABLE IF NOT EXISTS fornecedor (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  senha VARCHAR(255) NOT NULL,
  cnpj VARCHAR(14) NOT NULL,
  usuario_id INT NOT NULL,
  PRIMARY KEY (id),
  KEY idx_fornecedor_usuario (usuario_id),
  CONSTRAINT fk_fornecedor_usuario FOREIGN KEY (usuario_id) REFERENCES usuario (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

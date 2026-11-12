-- Execute UMA VEZ em bancos que já existiam antes das correções.
-- Ajuste o banco selecionado para o mesmo SMARTMEDS_DB_NAME em config.py.
-- Os registros legados sem proprietário serão atribuídos ao primeiro administrador
-- (ou ao primeiro usuário, se ainda não houver um administrador). Revise o resultado.

USE smartmeds3;
DELIMITER $$
DROP PROCEDURE IF EXISTS smartmeds_migrar_compatibilidade$$
CREATE PROCEDURE smartmeds_migrar_compatibilidade()
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'cliente' AND column_name = 'usuario_id'
  ) THEN
    ALTER TABLE cliente ADD COLUMN usuario_id INT NULL AFTER cnpj;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'localizacao' AND column_name = 'usuario_id'
  ) THEN
    ALTER TABLE localizacao ADD COLUMN usuario_id INT NULL AFTER andar;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'produto' AND column_name = 'usuario_id'
  ) THEN
    ALTER TABLE produto ADD COLUMN usuario_id INT NULL AFTER quantidade;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema = DATABASE() AND table_name = 'produto' AND column_name = 'precisa_temperatura_baixa'
  ) THEN
    ALTER TABLE produto ADD COLUMN precisa_temperatura_baixa TINYINT(1) NOT NULL DEFAULT 0 AFTER quantidade;
  END IF;

  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='sensor_leitura') THEN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND column_name='device_id') THEN
      ALTER TABLE sensor_leitura ADD COLUMN device_id VARCHAR(50) NOT NULL DEFAULT 'esp32-desconhecido';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND column_name='sensor') THEN
      ALTER TABLE sensor_leitura ADD COLUMN sensor VARCHAR(30) NOT NULL DEFAULT 'DHT11';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND column_name='temperatura') THEN
      ALTER TABLE sensor_leitura ADD COLUMN temperatura FLOAT NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND column_name='umidade') THEN
      ALTER TABLE sensor_leitura ADD COLUMN umidade FLOAT NULL;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND column_name='timestamp') THEN
      ALTER TABLE sensor_leitura ADD COLUMN timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP;
    END IF;
  END IF;
END$$
DELIMITER ;

CALL smartmeds_migrar_compatibilidade();
DROP PROCEDURE IF EXISTS smartmeds_migrar_compatibilidade;

SET @smartmeds_owner_id = (
  SELECT id FROM usuario WHERE LOWER(tipo) IN ('adm', 'admin') ORDER BY id LIMIT 1
);
SET @smartmeds_owner_id = COALESCE(@smartmeds_owner_id, (SELECT MIN(id) FROM usuario));

UPDATE cliente
SET usuario_id = @smartmeds_owner_id
WHERE (usuario_id IS NULL OR usuario_id = 0 OR usuario_id NOT IN (SELECT id FROM usuario))
  AND @smartmeds_owner_id IS NOT NULL;
UPDATE localizacao
SET usuario_id = @smartmeds_owner_id
WHERE (usuario_id IS NULL OR usuario_id = 0 OR usuario_id NOT IN (SELECT id FROM usuario))
  AND @smartmeds_owner_id IS NOT NULL;
UPDATE produto
SET usuario_id = @smartmeds_owner_id
WHERE (usuario_id IS NULL OR usuario_id = 0 OR usuario_id NOT IN (SELECT id FROM usuario))
  AND @smartmeds_owner_id IS NOT NULL;

-- Índices/relacionamentos adicionados só quando ainda não existem.
DELIMITER $$
DROP PROCEDURE IF EXISTS smartmeds_migrar_indices$$
CREATE PROCEDURE smartmeds_migrar_indices()
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='cliente' AND index_name='idx_cliente_usuario') THEN
    ALTER TABLE cliente ADD INDEX idx_cliente_usuario (usuario_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='localizacao' AND index_name='idx_localizacao_usuario') THEN
    ALTER TABLE localizacao ADD INDEX idx_localizacao_usuario (usuario_id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='produto' AND index_name='idx_produto_usuario') THEN
    ALTER TABLE produto ADD INDEX idx_produto_usuario (usuario_id);
  END IF;
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema=DATABASE() AND table_name='sensor_leitura') THEN
    IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND index_name='idx_sensor_timestamp') THEN
      ALTER TABLE sensor_leitura ADD INDEX idx_sensor_timestamp (sensor, timestamp);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.statistics WHERE table_schema=DATABASE() AND table_name='sensor_leitura' AND index_name='idx_device_timestamp') THEN
      ALTER TABLE sensor_leitura ADD INDEX idx_device_timestamp (device_id, timestamp);
    END IF;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.referential_constraints WHERE constraint_schema=DATABASE() AND table_name='cliente' AND constraint_name='fk_cliente_usuario') THEN
    ALTER TABLE cliente ADD CONSTRAINT fk_cliente_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.referential_constraints WHERE constraint_schema=DATABASE() AND table_name='localizacao' AND constraint_name='fk_localizacao_usuario') THEN
    ALTER TABLE localizacao ADD CONSTRAINT fk_localizacao_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id);
  END IF;
  IF NOT EXISTS (SELECT 1 FROM information_schema.referential_constraints WHERE constraint_schema=DATABASE() AND table_name='produto' AND constraint_name='fk_produto_usuario') THEN
    ALTER TABLE produto ADD CONSTRAINT fk_produto_usuario FOREIGN KEY (usuario_id) REFERENCES usuario(id);
  END IF;
END$$
DELIMITER ;

CALL smartmeds_migrar_indices();
DROP PROCEDURE IF EXISTS smartmeds_migrar_indices;

SELECT 'Migração concluída. Confira os proprietários dos dados legados antes de voltar a usar o sistema.' AS resultado;

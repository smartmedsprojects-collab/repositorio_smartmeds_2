-- Adiciona suporte à marcação de produtos que precisam de refrigeração.
-- Execute no MySQL Workbench usando o mesmo banco configurado em config.py.
-- A coluna é adicionada somente se ainda não existir; registros antigos recebem 0 (Não).
USE smartmeds3;
DELIMITER $$
DROP PROCEDURE IF EXISTS smartmeds_migrar_refrigeracao$$
CREATE PROCEDURE smartmeds_migrar_refrigeracao()
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = DATABASE()
      AND table_name = 'produto'
      AND column_name = 'precisa_temperatura_baixa'
  ) THEN
    ALTER TABLE produto
      ADD COLUMN precisa_temperatura_baixa TINYINT(1) NOT NULL DEFAULT 0 AFTER quantidade;
  END IF;
END$$
DELIMITER ;
CALL smartmeds_migrar_refrigeracao();
DROP PROCEDURE IF EXISTS smartmeds_migrar_refrigeracao;

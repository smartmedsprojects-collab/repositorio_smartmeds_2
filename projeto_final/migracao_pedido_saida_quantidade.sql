-- SmartMeds - ajuste do cabeçalho de pedido_saida para permitir pedido vazio.
-- Execute uma única vez no banco smartmeds3 (MySQL 8.0.16 ou superior).
-- A quantidade do cabeçalho é totalizada a partir de item_saida; por isso começa em 0.
-- A tabela item_saida continua exigindo quantidade maior que zero.

USE smartmeds3;

DELIMITER $$
DROP PROCEDURE IF EXISTS migrar_quantidade_pedido_saida_smartmeds$$
CREATE PROCEDURE migrar_quantidade_pedido_saida_smartmeds()
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema = DATABASE()
          AND table_name = 'pedido_saida'
          AND constraint_name = 'chk_pedido_saida_quantidade'
          AND constraint_type = 'CHECK'
    ) THEN
        ALTER TABLE pedido_saida
            DROP CHECK chk_pedido_saida_quantidade;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE constraint_schema = DATABASE()
          AND table_name = 'pedido_saida'
          AND constraint_name = 'chk_pedido_saida_quantidade_nao_negativa'
          AND constraint_type = 'CHECK'
    ) THEN
        ALTER TABLE pedido_saida
            ADD CONSTRAINT chk_pedido_saida_quantidade_nao_negativa
            CHECK (quantidade >= 0);
    END IF;

    ALTER TABLE pedido_saida
        MODIFY quantidade INT NOT NULL DEFAULT 0;
END$$
CALL migrar_quantidade_pedido_saida_smartmeds()$$
DROP PROCEDURE migrar_quantidade_pedido_saida_smartmeds$$
DELIMITER ;

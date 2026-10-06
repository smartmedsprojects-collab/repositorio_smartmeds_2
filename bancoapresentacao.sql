-- MySQL dump 10.13  Distrib 8.0.44, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: smartmeds3
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cliente`
--

DROP TABLE IF EXISTS `cliente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cliente` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `cnpj` varchar(14) NOT NULL,
  `usuario_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `cnpj` (`cnpj`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cliente`
--

LOCK TABLES `cliente` WRITE;
/*!40000 ALTER TABLE `cliente` DISABLE KEYS */;
INSERT INTO `cliente` VALUES (5,'Maria Luísa Joaquim Ortolan','maria.ortolan@aluno.senai.br','Malu@2009','89653219685329',15),(6,'Davi Rocha Ribeiro','davi.rocha@gmail.com','123456','85208953296845',15),(7,'Matheus de Jesus Toledo','matheus.toledo@gmail.com','2009','84521542445545',15);
/*!40000 ALTER TABLE `cliente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `funciousuario`
--

DROP TABLE IF EXISTS `funciousuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `funciousuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `admin_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_funciousuario_usuario` (`usuario_id`),
  CONSTRAINT `fk_funciousuario_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `funciousuario`
--

LOCK TABLES `funciousuario` WRITE;
/*!40000 ALTER TABLE `funciousuario` DISABLE KEYS */;
/*!40000 ALTER TABLE `funciousuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_entrada`
--

DROP TABLE IF EXISTS `item_entrada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_entrada` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `pedido_entrada_id` int DEFAULT NULL,
  `movimentacao_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_item_entrada_pedido` (`pedido_entrada_id`),
  KEY `fk_item_entrada_movimentacao` (`movimentacao_id`),
  CONSTRAINT `fk_item_entrada_movimentacao` FOREIGN KEY (`movimentacao_id`) REFERENCES `movimentacao` (`id`),
  CONSTRAINT `fk_item_entrada_pedido` FOREIGN KEY (`pedido_entrada_id`) REFERENCES `pedido_entrada` (`id_pedido_entrada`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_entrada`
--

LOCK TABLES `item_entrada` WRITE;
/*!40000 ALTER TABLE `item_entrada` DISABLE KEYS */;
/*!40000 ALTER TABLE `item_entrada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `item_saida`
--

DROP TABLE IF EXISTS `item_saida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `item_saida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `pedido_saida_id` int DEFAULT NULL,
  `movimentacao_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_item_saida_pedido` (`pedido_saida_id`),
  KEY `fk_item_saida_movimentacao` (`movimentacao_id`),
  CONSTRAINT `fk_item_saida_movimentacao` FOREIGN KEY (`movimentacao_id`) REFERENCES `movimentacao` (`id`),
  CONSTRAINT `fk_item_saida_pedido` FOREIGN KEY (`pedido_saida_id`) REFERENCES `pedido_saida` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `item_saida`
--

LOCK TABLES `item_saida` WRITE;
/*!40000 ALTER TABLE `item_saida` DISABLE KEYS */;
INSERT INTO `item_saida` VALUES (1,3,300.00,4,3),(2,20,2000.00,5,4),(3,20,200.00,6,5),(4,200,2000.00,7,6),(5,20,2000.00,8,7),(6,20,2000.00,9,8),(7,20,2000.00,10,9),(8,20,200.00,11,10),(9,10,100.00,12,11);
/*!40000 ALTER TABLE `item_saida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `localizacao`
--

DROP TABLE IF EXISTS `localizacao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `localizacao` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rua` varchar(100) NOT NULL,
  `numero` varchar(10) NOT NULL,
  `andar` varchar(20) DEFAULT NULL,
  `usuario_id` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `localizacao`
--

LOCK TABLES `localizacao` WRITE;
/*!40000 ALTER TABLE `localizacao` DISABLE KEYS */;
INSERT INTO `localizacao` VALUES (1,'rua tal','1','12',15),(2,'senai','1','2',15);
/*!40000 ALTER TABLE `localizacao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `movimentacao`
--

DROP TABLE IF EXISTS `movimentacao`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `movimentacao` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo_movimentacao` varchar(50) DEFAULT NULL,
  `data_movimentacao` datetime DEFAULT NULL,
  `quantidade` int NOT NULL,
  `quantidade_min` int DEFAULT NULL,
  `produto_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_movimentacao_produto` (`produto_id`),
  CONSTRAINT `fk_movimentacao_produto` FOREIGN KEY (`produto_id`) REFERENCES `produto` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `movimentacao`
--

LOCK TABLES `movimentacao` WRITE;
/*!40000 ALTER TABLE `movimentacao` DISABLE KEYS */;
INSERT INTO `movimentacao` VALUES (2,'ENTRADA','2026-10-06 08:47:20',200,NULL,38),(3,'SAIDA','2026-10-06 08:49:40',3,NULL,38),(4,'SAIDA','2026-10-06 09:01:28',20,NULL,38),(5,'SAIDA','2026-10-06 09:03:58',20,NULL,38),(6,'SAIDA','2026-10-06 09:07:58',200,NULL,38),(7,'SAIDA','2026-10-06 09:19:15',20,NULL,38),(8,'SAIDA','2026-10-06 09:24:52',20,NULL,38),(9,'SAIDA','2026-10-06 09:27:33',20,NULL,38),(10,'SAIDA','2026-10-06 09:32:33',20,NULL,38),(11,'SAIDA','2026-10-06 10:09:58',10,NULL,38);
/*!40000 ALTER TABLE `movimentacao` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_entrada`
--

DROP TABLE IF EXISTS `pedido_entrada`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_entrada` (
  `id_pedido_entrada` int NOT NULL AUTO_INCREMENT,
  `numero_documento` varchar(50) DEFAULT NULL,
  `fornecedor` varchar(100) DEFAULT NULL,
  `data_entrada` date NOT NULL,
  `usuario_id` int NOT NULL,
  `observacao` text,
  `status` varchar(30) DEFAULT 'aberto',
  `criado_em` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_pedido_entrada`),
  KEY `fk_pedido_entrada_usuario` (`usuario_id`),
  CONSTRAINT `fk_pedido_entrada_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_entrada`
--

LOCK TABLES `pedido_entrada` WRITE;
/*!40000 ALTER TABLE `pedido_entrada` DISABLE KEYS */;
INSERT INTO `pedido_entrada` VALUES (1,'003','Droga Raia','2026-10-01',15,'teste','ABERTO','2026-10-01 14:55:24'),(2,'0123','Cristalia','2026-10-06',15,'teste','ABERTO','2026-10-06 08:48:31'),(3,'006','Bairral','2026-10-06',15,'','ABERTO','2026-10-06 09:07:09'),(4,'2026','Guilherme','2026-10-06',15,'testeeeee','PENDENTE','2026-10-06 09:18:34');
/*!40000 ALTER TABLE `pedido_entrada` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pedido_saida`
--

DROP TABLE IF EXISTS `pedido_saida`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pedido_saida` (
  `id` int NOT NULL AUTO_INCREMENT,
  `tipo` varchar(50) DEFAULT NULL,
  `pagamento` varchar(50) DEFAULT NULL,
  `quantidade` int NOT NULL,
  `valor` decimal(10,2) DEFAULT NULL,
  `data_pagamento` date DEFAULT NULL,
  `cliente_id` int DEFAULT NULL,
  `usuario_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_pedido_saida_cliente` (`cliente_id`),
  KEY `fk_pedido_saida_usuario` (`usuario_id`),
  CONSTRAINT `fk_pedido_saida_cliente` FOREIGN KEY (`cliente_id`) REFERENCES `cliente` (`id`),
  CONSTRAINT `fk_pedido_saida_usuario` FOREIGN KEY (`usuario_id`) REFERENCES `usuario` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pedido_saida`
--

LOCK TABLES `pedido_saida` WRITE;
/*!40000 ALTER TABLE `pedido_saida` DISABLE KEYS */;
INSERT INTO `pedido_saida` VALUES (1,'VENDA','DINHEIRO',20,2000.00,'2026-10-01',6,15),(2,'DOACAO','CARTAO',15,2000.00,'2026-10-01',6,15),(3,'DOACAO','PIX',5,2550.00,'2026-11-07',6,15),(4,'VENDA','PIX',20,2000.00,'2027-02-01',6,15),(5,'VENDA','DINHEIRO',200,20000.00,'2026-10-23',6,15),(6,'VENDA','BOLETO',20,200.00,'2026-10-19',6,15),(7,'VENDA','BOLETO',200,2000.00,'2026-10-06',6,15),(8,'VENDA','CARTAO',20,2000.00,'2026-10-12',7,15),(9,'VENDA','PIX',20,2000.00,'2026-10-12',7,15),(10,'VENDA','CARTAO',20,2000.00,'2026-10-12',7,15),(11,'DOACAO','CARTAO',20,200.00,'2026-10-12',7,15),(12,'VENDA','CARTAO',10,2000.00,'2026-10-12',6,15);
/*!40000 ALTER TABLE `pedido_saida` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `produto`
--

DROP TABLE IF EXISTS `produto`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `produto` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `marca` varchar(100) DEFAULT NULL,
  `data_de_validade` date DEFAULT NULL,
  `especificacao` text,
  `unidade_medida` varchar(50) DEFAULT NULL,
  `localizacao_id` int DEFAULT NULL,
  `quantidade` int NOT NULL DEFAULT '0',
  `usuario_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_produto_localizacao` (`localizacao_id`),
  CONSTRAINT `fk_produto_localizacao` FOREIGN KEY (`localizacao_id`) REFERENCES `localizacao` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `produto`
--

LOCK TABLES `produto` WRITE;
/*!40000 ALTER TABLE `produto` DISABLE KEYS */;
INSERT INTO `produto` VALUES (38,'Dipirona','Medley','2036-01-05','500 gramas','Comprimido / Cápsula',2,110,15);
/*!40000 ALTER TABLE `produto` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nome` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `senha` varchar(255) NOT NULL,
  `tipo` varchar(20) NOT NULL,
  `identificacao` varchar(20) NOT NULL,
  `permissao` tinyint NOT NULL DEFAULT '0',
  `foto_nome` varchar(255) DEFAULT NULL,
  `foto_caminho` varchar(500) DEFAULT NULL,
  `foto_blob` blob,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (15,'Maria Luisa Joaquim Ortolan','maria.ortolan@gmail.com','$2b$12$tiRXB3QHWihoKxnb9FXNT.ULo9805HEkEur.Hdd3FZPqMUkTVq2QK','adm','006',0,NULL,NULL,NULL),(27,'Matheus de Jesus Toledo','matheus.toledo@gmail.com','$2b$12$RILTES6UW3Q0KenGNRNKn.3IfBsVSbp53JuS8l0H0gnUoqAJct1qG','adm','2903',0,NULL,NULL,NULL),(28,'Davi Rocha Ribeiro','davi.rocha@gmail.com','$2b$12$Yilq5aO8KYLteRZfphGjO.GQYRNnYilQ3uNafWpVLY/p6KuGWg0QK','adm','1912',0,NULL,NULL,NULL),(29,'Nathan Elias Padim Ferreira','nathan.pardim@gmail.com','$2b$12$OC4ve0M9IR1kJQmdSp34huTE4E8L33.veD69B7PT8j55In5Bp51zS','consulta','1409',0,NULL,NULL,NULL),(30,'Samuel Rodrigues Ferreira','samuel.rodrigues@gmail.com','$2b$12$JQ/gQYVuObzb.Z4ksT9WquishKgai55c0iFPplvOIqIZFBcgfuJp.','estoquista','0106',0,NULL,NULL,NULL),(31,'Guilherme Jesuino Marques','guilherme@gmail.com','$2b$12$joAU64.vX1vIuqBsXz0YN..Pi2C2L21HhIb2TZlKk5YVzS62QJIu6','adm','2702',0,NULL,NULL,NULL);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-06 11:40:06

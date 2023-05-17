-- MySQL dump 10.16  Distrib 10.1.48-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: db
-- ------------------------------------------------------
-- Server version	10.1.48-MariaDB-0+deb9u2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `menu` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(8) DEFAULT NULL,
  `url` varchar(8) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
INSERT INTO `menu` VALUES (2,'დამატება','/add'),(3,'სია','/all'),(5,'საწყობი','/storage'),(6,'გასვლა','/logout');
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `purcell`
--

DROP TABLE IF EXISTS `purcell`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `purcell` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `sender` varchar(50) DEFAULT NULL,
  `sender_phone` varchar(50) DEFAULT NULL,
  `recipient` varchar(50) DEFAULT NULL,
  `recipient_phone` varchar(50) DEFAULT NULL,
  `inventory` text,
  `cost` varchar(50) DEFAULT NULL,
  `passport` varchar(50) DEFAULT NULL,
  `weight` varchar(50) DEFAULT NULL,
  `responsibility` varchar(50) DEFAULT NULL,
  `number` tinyint(4) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `date` varchar(50) DEFAULT NULL,
  `flight` varchar(50) DEFAULT NULL,
  `image` varchar(50) DEFAULT NULL,
  `extradition` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `purcell`
--

LOCK TABLES `purcell` WRITE;
/*!40000 ALTER TABLE `purcell` DISABLE KEYS */;
INSERT INTO `purcell` VALUES (1,'DIMA JIOSHVILI','571 17 17 17','EJEJJE EJEJJRJ','0459404909','mokle dana erti xanjali da tanki','+150L','685888558','105KG','150L',1,'Moscow','2023-05-14','2023-05-03','static/images/1-2023-05-03.jpeg',''),(2,'MAKSIM CHERNYKH','599599599599','ANASTASIIA GOOGE','3495349053090','AR VIOCI RA DEVS DA ARC MAINTERESEBS  шуццшущшцгат уацуагшцтацу тцшутцшгтуашгт тшцутшацтшт шгтцушатшгтш тшгцтуашгцтшг штцушгатцуаштш тцшгутшгтцу уацу ацу уау ацу цуацуа цацуа цуау ац уацу ацуцацац ауцауа цуацуа цуацуац ац цуццацуаца а цацацауац ацацацуцу   цуацауцуацуа цуацуа цуацуаацуа цуацуацуауацацуаау','+150L','34895345','15KG','200L',2,'S.P.B','2023-05-15','2023-05-03','static/images/2-2023-05-03.jpeg',''),(3,'MAKSIM BARANCHIKOV SED','hbb','IIBI','uhiuhiu','HIUHUH','IUWRRG','UIHUIH','IUHUIHIU','HIUH',3,'Moscow','2023-05-15','2023-05-03','static/images/3-2023-05-03.jpeg','');
/*!40000 ALTER TABLE `purcell` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` INT PRIMARY KEY AUTO_INCREMENT,
  `login` varchar(13) DEFAULT NULL,
  `psw` varchar(102) DEFAULT NULL,
  `role` varchar(5) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'viptour','pbkdf2:sha256:260000$XZyCuXepqwZQE4o4$5927484b023d6800f6e41cca9f655eb7805040098db87804266ddb723b4f911e','admin'),(2,'VipTourMoscow','pbkdf2:sha256:260000$SQ1qZl5NdHnrctMP$4339a35798995e70757b1fe4de4d8e4b18c9672bd1bbb771cb3cbcaec101af7b','user'),(3,'VipTourS.P.B','pbkdf2:sha256:260000$HIZJSverEnaqDUoh$8c23da6c93f50c89d8e1b6c6f61e4ffe29ac04bb81caa564ffcde158cbee5169','user');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-12-29 11:52:07

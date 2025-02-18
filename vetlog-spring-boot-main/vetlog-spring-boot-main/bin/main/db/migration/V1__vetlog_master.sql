-- MySQL dump 10.13  Distrib 5.7.18, for Linux (x86_64)
--
-- Host: localhost    Database: vetlog_spring_boot
-- ------------------------------------------------------
-- Server version	5.7.18-0ubuntu0.17.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `registration_code`
--

DROP TABLE IF EXISTS `registration_code`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `registration_code` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date_created` datetime NOT NULL,
  `email` varchar(255) NOT NULL,
  `status` int(11) NOT NULL,
  `token` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registration_code`
--

LOCK TABLES `registration_code` WRITE;
/*!40000 ALTER TABLE `registration_code` DISABLE KEYS */;
/*!40000 ALTER TABLE `registration_code` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `breed`
--

DROP TABLE IF EXISTS `breed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `breed` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date_created` datetime NOT NULL,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=70 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `breed`
--

LOCK TABLES `breed` WRITE;
/*!40000 ALTER TABLE `breed` DISABLE KEYS */;
INSERT INTO `breed` VALUES (1,'2017-06-03 21:23:01','Labrador','DOG'),(2,'2017-06-03 21:23:01','Landrace','DOG'),(3,'2017-06-03 21:23:01','German Shepherd','DOG'),(4,'2017-06-03 21:23:01','Golden Retriever','DOG'),(5,'2017-06-03 21:23:01','Bulldog','DOG'),(6,'2017-06-03 21:23:01','Poodle','DOG'),(7,'2017-06-03 21:23:01','Beagle','DOG'),(8,'2017-06-03 21:23:01','Boxer','DOG'),(9,'2017-06-03 21:23:01','Yorkshire Terrier','DOG'),(10,'2017-06-03 21:23:01','Rottweiler','DOG'),(11,'2017-06-03 21:23:01','Chihuahua','DOG'),(12,'2017-06-03 21:23:01','Dachshund','DOG'),(13,'2017-06-03 21:23:01','French Bulldog','DOG'),(14,'2017-06-03 21:23:01','Shih Tzu','DOG'),(15,'2017-06-03 21:23:01','Pug','DOG'),(16,'2017-06-03 21:23:01','Siberian Husky','DOG'),(17,'2017-06-03 21:23:01','English Cocker Spaniel','DOG'),(18,'2017-06-03 21:23:01','Pomeranian','DOG'),(19,'2017-06-03 21:23:01','Cavalier King Charles Spaniel','DOG'),(20,'2017-06-03 21:23:01','Border Collie','DOG'),(21,'2017-06-03 21:23:01','Bull Terrier','DOG'),(22,'2017-06-03 21:23:01','Schnauzer','DOG'),(23,'2017-06-03 21:23:01','Great Dane','DOG'),(24,'2017-06-03 21:23:01','Bull Terrier','DOG'),(25,'2017-06-03 21:23:01','Old English Sheepdog','DOG'),(26,'2017-06-03 21:23:01','Doberman','DOG'),(27,'2017-06-03 21:23:01','Jack Russell Terrier','DOG'),(28,'2017-06-03 21:23:01','Maltese','DOG'),(29,'2017-06-03 21:23:01','Newfoundland dog','DOG'),(30,'2017-06-03 21:23:01','English Mastiff','DOG'),(31,'2017-06-03 21:23:01','Australian Shepherd','DOG'),(32,'2017-06-03 21:23:01','Boston Terrier','DOG'),(33,'2017-06-03 21:23:01','Havanese','DOG'),(34,'2017-06-03 21:23:01','Dalmatian','DOG'),(35,'2017-06-03 21:23:01','Pointer','DOG'),(36,'2017-06-03 21:23:01','St. Bernard','DOG'),(37,'2017-06-03 21:23:01','Pit bull','DOG'),(38,'2017-06-03 21:23:01','Weimaraner','DOG'),(39,'2017-06-03 21:23:01','Dogue de Bordeaux','DOG'),(40,'2017-06-03 21:23:01','Siamese','CAT'),(41,'2017-06-03 21:23:01','Landrace','CAT'),(42,'2017-06-03 21:23:01','British Shorthair','CAT'),(43,'2017-06-03 21:23:01','Persian','CAT'),(44,'2017-06-03 21:23:01','Maine Coon','CAT'),(45,'2017-06-03 21:23:01','Ragdoll','CAT'),(46,'2017-06-03 21:23:01','American Shorthair','CAT'),(47,'2017-06-03 21:23:01','Abyssinian','CAT'),(48,'2017-06-03 21:23:01','Burmese','CAT'),(49,'2017-06-03 21:23:01','Bengal','CAT'),(50,'2017-06-03 21:23:01','Sphynx','CAT'),(51,'2017-06-03 21:23:01','Birman','CAT'),(52,'2017-06-03 21:23:01','Scottish Fold','CAT'),(53,'2017-06-03 21:23:01','American Bobtail','CAT'),(54,'2017-06-03 21:23:01','Chicken','BIRD'),(55,'2017-06-03 21:23:01','Canary','BIRD'),(56,'2017-06-03 21:23:01','Duck','BIRD'),(57,'2017-06-03 21:23:01','Dove','BIRD'),(58,'2017-06-03 21:23:01','Goose','BIRD'),(59,'2017-06-03 21:23:01','Swan','BIRD'),(60,'2017-06-03 21:23:01','Guinea pig','RODENT'),(61,'2017-06-03 21:23:01','Hamster','RODENT'),(62,'2017-06-03 21:23:01','Chinchillas','RODENT'),(63,'2017-06-03 21:23:01','Rabbit','RODENT'),(64,'2017-06-03 21:23:01','Corn Snake','SNAKE'),(65,'2017-06-03 21:23:01','Kingsnake','SNAKE'),(66,'2017-06-03 21:23:01','Rosy Boa','SNAKE'),(67,'2017-06-03 21:23:01','Gopher','SNAKE'),(68,'2017-06-03 21:23:01','Ball Python','SNAKE'),(69,'2017-06-03 21:23:01','Tarantula','SPIDER');
/*!40000 ALTER TABLE `breed` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `account_non_expired` bit(1) NOT NULL,
  `account_non_locked` bit(1) NOT NULL,
  `credentials_non_expired` bit(1) NOT NULL,
  `date_created` datetime NOT NULL,
  `email` varchar(255) DEFAULT NULL,
  `enabled` bit(1) NOT NULL,
  `mobile` varchar(255) DEFAULT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(255) NOT NULL,
  `username` varchar(255) NOT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_sb8bbouer5wak8vyiiy4pf2bx` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

--
-- Table structure for table `pet`
--

DROP TABLE IF EXISTS `pet`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pet` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `birth_date` datetime NOT NULL,
  `date_created` datetime NOT NULL,
  `dewormed` bit(1) NOT NULL,
  `name` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `sterilized` bit(1) NOT NULL,
  `uuid` varchar(255) NOT NULL,
  `vaccinated` bit(1) NOT NULL,
  `adopter_id` bigint(20) DEFAULT NULL,
  `breed_id` bigint(20) DEFAULT NULL,
  `user_id` bigint(20) DEFAULT NULL,
  `pet_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKj3j9664ee510hnt2pkd7on7dl` (`adopter_id`),
  KEY `FKiqbjbaml7gtwulqptktmsi5dc` (`breed_id`),
  KEY `FK9hxka0oqkd15dmqstdarori08` (`user_id`),
  CONSTRAINT `FK9hxka0oqkd15dmqstdarori08` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `FKiqbjbaml7gtwulqptktmsi5dc` FOREIGN KEY (`breed_id`) REFERENCES `breed` (`id`),
  CONSTRAINT `FKj3j9664ee510hnt2pkd7on7dl` FOREIGN KEY (`adopter_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pet`
--


--
-- Table structure for table `pet_adoption`
--

DROP TABLE IF EXISTS `pet_adoption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pet_adoption` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `description` text NOT NULL,
  `pet_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK939up3l91l7c779k1qlg9qhul` (`pet_id`),
  CONSTRAINT `FK939up3l91l7c779k1qlg9qhul` FOREIGN KEY (`pet_id`) REFERENCES `pet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pet_adoption`
--

LOCK TABLES `pet_adoption` WRITE;
/*!40000 ALTER TABLE `pet_adoption` DISABLE KEYS */;
/*!40000 ALTER TABLE `pet_adoption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pet_image`
--

DROP TABLE IF EXISTS `pet_image`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pet_image` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `uuid` varchar(255) NOT NULL,
  `pet_image_id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FKnf9loskcjkxo9f2qafq08dyvp` (`pet_image_id`),
  CONSTRAINT `FKnf9loskcjkxo9f2qafq08dyvp` FOREIGN KEY (`pet_image_id`) REFERENCES `pet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pet_image`
--

LOCK TABLES `pet_image` WRITE;
/*!40000 ALTER TABLE `pet_image` DISABLE KEYS */;
/*!40000 ALTER TABLE `pet_image` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pet_log`
--

DROP TABLE IF EXISTS `pet_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pet_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date_created` datetime NOT NULL,
  `diagnosis` varchar(1000) NOT NULL,
  `medicine` varchar(1000) DEFAULT NULL,
  `signs` varchar(1000) NOT NULL,
  `vet_name` varchar(255) DEFAULT NULL,
  `pet_id` bigint(20) DEFAULT NULL,
  `uuid` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `FK6qt0o586ujuoupfj1gnnw3yjp` (`pet_id`),
  CONSTRAINT `FK6qt0o586ujuoupfj1gnnw3yjp` FOREIGN KEY (`pet_id`) REFERENCES `pet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pet_log`
--

LOCK TABLES `pet_log` WRITE;
/*!40000 ALTER TABLE `pet_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `pet_log` ENABLE KEYS */;
UNLOCK TABLES;

DROP TABLE IF EXISTS `pet_medicine`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pet_medicine` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `uuid` varchar(255) NOT NULL,
    `pet_medicine_id` bigint(20) DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `FKnf9loskcjkxo9f2qafq08dyjm` (`pet_medicine_id`),
    CONSTRAINT `FKnf9loskcjkxo9f2qafq08dyjm` FOREIGN KEY (`pet_medicine_id`) REFERENCES `pet` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

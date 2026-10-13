-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: digital_library
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `digital_library`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `digital_library` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `digital_library`;

--
-- Table structure for table `authors`
--

DROP TABLE IF EXISTS `authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `authors` (
  `author_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `bio` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`author_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `authors`
--

LOCK TABLES `authors` WRITE;
/*!40000 ALTER TABLE `authors` DISABLE KEYS */;
INSERT INTO `authors` VALUES (1,'George Orwell',NULL),(2,'Yuval Noah Harari',NULL),(3,'Robert C. Martin',NULL),(4,'Paul Deitel',NULL),(5,'Harper Lee',NULL),(6,'Paulo Coelho',NULL),(7,'Luciano Ramalho',NULL);
/*!40000 ALTER TABLE `authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_authors`
--

DROP TABLE IF EXISTS `book_authors`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_authors` (
  `book_id` int NOT NULL,
  `author_id` int NOT NULL,
  PRIMARY KEY (`book_id`,`author_id`),
  KEY `author_id` (`author_id`),
  CONSTRAINT `book_authors_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE,
  CONSTRAINT `book_authors_ibfk_2` FOREIGN KEY (`author_id`) REFERENCES `authors` (`author_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_authors`
--

LOCK TABLES `book_authors` WRITE;
/*!40000 ALTER TABLE `book_authors` DISABLE KEYS */;
INSERT INTO `book_authors` VALUES (1,1),(2,2),(7,2),(3,3),(4,4),(5,5),(6,6),(8,7);
/*!40000 ALTER TABLE `book_authors` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `book_copies`
--

DROP TABLE IF EXISTS `book_copies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `book_copies` (
  `copy_id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `barcode` varchar(30) COLLATE utf8mb4_unicode_ci NOT NULL,
  `shelf_location` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` enum('Available','Issued','Reserved','Lost','Damaged') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Available',
  `acquired_on` date NOT NULL DEFAULT (curdate()),
  PRIMARY KEY (`copy_id`),
  UNIQUE KEY `barcode` (`barcode`),
  KEY `idx_copies_book_status` (`book_id`,`status`),
  CONSTRAINT `book_copies_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `book_copies`
--

LOCK TABLES `book_copies` WRITE;
/*!40000 ALTER TABLE `book_copies` DISABLE KEYS */;
INSERT INTO `book_copies` VALUES (1,1,'BC-0001-1','S5-1','Available','2026-10-07'),(2,1,'BC-0001-2','S5-2','Issued','2026-10-07'),(3,1,'BC-0001-3','S5-3','Available','2026-10-07'),(4,2,'BC-0002-1','S2-1','Available','2026-10-07'),(5,2,'BC-0002-2','S2-2','Available','2026-10-07'),(6,2,'BC-0002-3','S2-3','Available','2026-10-07'),(7,3,'BC-0003-1','S3-1','Available','2026-10-07'),(8,3,'BC-0003-2','S3-2','Available','2026-10-07'),(9,3,'BC-0003-3','S3-3','Available','2026-10-07'),(10,4,'BC-0004-1','S3-1','Issued','2026-10-07'),(11,4,'BC-0004-2','S3-2','Available','2026-10-07'),(12,4,'BC-0004-3','S3-3','Available','2026-10-07'),(13,5,'BC-0005-1','S5-1','Issued','2026-10-07'),(14,5,'BC-0005-2','S5-2','Available','2026-10-07'),(15,5,'BC-0005-3','S5-3','Available','2026-10-07'),(16,6,'BC-0006-1','S1-1','Issued','2026-10-07'),(17,6,'BC-0006-2','S1-2','Available','2026-10-07'),(18,6,'BC-0006-3','S1-3','Available','2026-10-07'),(19,7,'BC-0007-1','S2-1','Available','2026-10-07'),(20,7,'BC-0007-2','S2-2','Available','2026-10-07'),(21,7,'BC-0007-3','S2-3','Lost','2026-10-07'),(22,8,'BC-0008-1','S3-1','Available','2026-10-07'),(23,8,'BC-0008-2','S3-2','Available','2026-10-07'),(24,8,'BC-0008-3','S3-3','Damaged','2026-10-07');
/*!40000 ALTER TABLE `book_copies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `books`
--

DROP TABLE IF EXISTS `books`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `books` (
  `book_id` int NOT NULL AUTO_INCREMENT,
  `isbn` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `publisher_id` int NOT NULL,
  `category_id` int NOT NULL,
  `publication_year` smallint DEFAULT NULL,
  `edition` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT '1st',
  `language` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT 'English',
  `price` decimal(8,2) NOT NULL DEFAULT '0.00',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`book_id`),
  UNIQUE KEY `isbn` (`isbn`),
  KEY `fk_books_pub` (`publisher_id`),
  KEY `fk_books_cat` (`category_id`),
  KEY `idx_books_title` (`title`),
  CONSTRAINT `fk_books_cat` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  CONSTRAINT `fk_books_pub` FOREIGN KEY (`publisher_id`) REFERENCES `publishers` (`publisher_id`),
  CONSTRAINT `chk_books_price` CHECK ((`price` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `books`
--

LOCK TABLES `books` WRITE;
/*!40000 ALTER TABLE `books` DISABLE KEYS */;
INSERT INTO `books` VALUES (1,'9780451524935','1984',1,5,1949,'1st','English',350.00,'2026-10-07 04:03:24'),(2,'9780062316097','Sapiens',2,2,2015,'1st','English',499.00,'2026-10-07 04:03:24'),(3,'9780132350884','Clean Code',4,3,2008,'1st','English',650.00,'2026-10-07 04:03:24'),(4,'9780135404676','Python How to Program',4,3,2019,'1st','English',720.00,'2026-10-07 04:03:24'),(5,'9780061120084','To Kill a Mockingbird',2,5,1960,'1st','English',320.00,'2026-10-07 04:03:24'),(6,'9780062315007','The Alchemist',2,1,1988,'1st','English',280.00,'2026-10-07 04:03:24'),(7,'9780062464316','Homo Deus',2,2,2017,'1st','English',520.00,'2026-10-07 04:03:24'),(8,'9781492052203','Fluent Python',3,3,2022,'1st','English',890.00,'2026-10-07 04:03:24');
/*!40000 ALTER TABLE `books` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `categories`
--

DROP TABLE IF EXISTS `categories`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `categories` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`category_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `categories`
--

LOCK TABLES `categories` WRITE;
/*!40000 ALTER TABLE `categories` DISABLE KEYS */;
INSERT INTO `categories` VALUES (5,'Classics'),(1,'Fiction'),(2,'History'),(4,'Self Help'),(3,'Technology');
/*!40000 ALTER TABLE `categories` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fines`
--

DROP TABLE IF EXISTS `fines`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `fines` (
  `fine_id` int NOT NULL AUTO_INCREMENT,
  `issue_id` int NOT NULL,
  `member_id` int NOT NULL,
  `days_overdue` int NOT NULL DEFAULT '0',
  `amount` decimal(10,2) NOT NULL,
  `reason` enum('Overdue','Damaged','Lost') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Overdue',
  `status` enum('Unpaid','Paid','Waived') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Unpaid',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `paid_on` datetime DEFAULT NULL,
  PRIMARY KEY (`fine_id`),
  UNIQUE KEY `issue_id` (`issue_id`),
  KEY `idx_fines_member_status` (`member_id`,`status`),
  CONSTRAINT `fines_ibfk_1` FOREIGN KEY (`issue_id`) REFERENCES `issues` (`issue_id`),
  CONSTRAINT `fines_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fines`
--

LOCK TABLES `fines` WRITE;
/*!40000 ALTER TABLE `fines` DISABLE KEYS */;
INSERT INTO `fines` VALUES (1,1,1,6,30.00,'Overdue','Waived','2026-10-07 04:03:24','2026-10-07 09:38:53');
/*!40000 ALTER TABLE `fines` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `issues`
--

DROP TABLE IF EXISTS `issues`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `issues` (
  `issue_id` int NOT NULL AUTO_INCREMENT,
  `copy_id` int NOT NULL,
  `member_id` int NOT NULL,
  `issue_date` date NOT NULL,
  `due_date` date NOT NULL,
  `return_date` date DEFAULT NULL,
  `status` enum('Issued','Overdue','Returned') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Issued',
  `return_condition` enum('Good','Damaged','Lost') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`issue_id`),
  KEY `idx_issues_member` (`member_id`,`return_date`),
  KEY `idx_issues_copy` (`copy_id`,`return_date`),
  CONSTRAINT `issues_ibfk_1` FOREIGN KEY (`copy_id`) REFERENCES `book_copies` (`copy_id`),
  CONSTRAINT `issues_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`),
  CONSTRAINT `chk_issue_dates` CHECK ((`due_date` >= `issue_date`))
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `issues`
--

LOCK TABLES `issues` WRITE;
/*!40000 ALTER TABLE `issues` DISABLE KEYS */;
INSERT INTO `issues` VALUES (1,1,1,'2026-08-28','2026-09-11','2026-09-17','Returned','Good'),(2,4,2,'2026-09-07','2026-09-21','2026-09-19','Returned','Good'),(3,7,3,'2026-09-12','2026-09-26','2026-09-25','Returned','Good'),(4,1,2,'2026-09-22','2026-10-06','2026-10-02','Returned','Good'),(5,10,4,'2026-09-27','2026-10-11',NULL,'Issued',NULL),(6,13,5,'2026-09-07','2026-09-21',NULL,'Overdue',NULL),(7,2,3,'2026-10-02','2026-10-16',NULL,'Issued',NULL),(8,16,6,'2026-10-04','2026-10-18',NULL,'Issued',NULL);
/*!40000 ALTER TABLE `issues` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_issues_bi` BEFORE INSERT ON `issues` FOR EACH ROW BEGIN
    DECLARE m_status  VARCHAR(20);
    DECLARE m_expires DATE;

    SELECT status, expires_on INTO m_status, m_expires
      FROM members WHERE member_id = NEW.member_id;

    IF m_status IS NULL OR m_status <> 'Active' OR m_expires < CURDATE() THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member is not active or membership has expired';
    END IF;
    IF fn_member_active_loans(NEW.member_id) >= fn_setting('max_loans') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member has reached the maximum number of active loans';
    END IF;
    IF fn_member_unpaid_fines(NEW.member_id) >= fn_setting('fine_block_limit') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member has unpaid fines above the allowed limit';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_issues_ai` AFTER INSERT ON `issues` FOR EACH ROW BEGIN
    UPDATE book_copies SET status = 'Issued' WHERE copy_id = NEW.copy_id;

    INSERT INTO notifications (member_id, issue_id, type, subject, message)
    SELECT NEW.member_id, NEW.issue_id, 'Issue Confirmation',
           CONCAT('Book issued: ', b.title),
           CONCAT('Dear ', m.full_name, ', "', b.title, '" has been issued to you. Due date: ',
                  DATE_FORMAT(NEW.due_date, '%d %b %Y'), '.')
      FROM book_copies c
      JOIN books b   ON b.book_id = c.book_id
      JOIN members m ON m.member_id = NEW.member_id
     WHERE c.copy_id = NEW.copy_id;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_issues_bu` BEFORE UPDATE ON `issues` FOR EACH ROW BEGIN
    IF OLD.return_date IS NULL AND NEW.return_date IS NOT NULL THEN
        IF NEW.return_date < OLD.issue_date THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Return date cannot be before the issue date';
        END IF;
        SET NEW.status = 'Returned';
        IF NEW.return_condition IS NULL THEN
            SET NEW.return_condition = 'Good';
        END IF;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `trg_issues_au` AFTER UPDATE ON `issues` FOR EACH ROW BEGIN
    DECLARE v_title  VARCHAR(200);
    DECLARE v_price  DECIMAL(8,2);
    DECLARE v_name   VARCHAR(120);
    DECLARE v_days   INT;
    DECLARE v_amount DECIMAL(10,2);
    DECLARE v_reason VARCHAR(10) DEFAULT 'Overdue';

    IF OLD.return_date IS NULL AND NEW.return_date IS NOT NULL THEN
        SELECT b.title, b.price INTO v_title, v_price
          FROM book_copies c JOIN books b ON b.book_id = c.book_id
         WHERE c.copy_id = NEW.copy_id;
        SELECT full_name INTO v_name FROM members WHERE member_id = NEW.member_id;

        SET v_days   = GREATEST(DATEDIFF(NEW.return_date, NEW.due_date), 0);
        SET v_amount = fn_calc_fine(NEW.due_date, NEW.return_date);

        IF NEW.return_condition = 'Lost' THEN
            SET v_amount = v_amount + v_price;
            SET v_reason = 'Lost';
        ELSEIF NEW.return_condition = 'Damaged' THEN
            SET v_amount = v_amount + ROUND(v_price * 0.5, 2);
            SET v_reason = 'Damaged';
        END IF;

        IF v_amount > 0 THEN
            INSERT INTO fines (issue_id, member_id, days_overdue, amount, reason)
            VALUES (NEW.issue_id, NEW.member_id, v_days, v_amount, v_reason);

            INSERT INTO notifications (member_id, issue_id, type, subject, message)
            VALUES (NEW.member_id, NEW.issue_id, 'Fine Notice',
                    CONCAT('Fine charged: ', v_title),
                    CONCAT('Dear ', v_name, ', a fine of ', v_amount, ' (', v_reason, ', ',
                           v_days, ' day(s) late) was charged for "', v_title, '".'));
        END IF;

        IF NEW.return_condition = 'Lost' THEN
            UPDATE book_copies SET status = 'Lost' WHERE copy_id = NEW.copy_id;
        ELSEIF NEW.return_condition = 'Damaged' THEN
            UPDATE book_copies SET status = 'Damaged' WHERE copy_id = NEW.copy_id;
        ELSE
            CALL sp_release_copy(NEW.copy_id);
        END IF;

        INSERT INTO notifications (member_id, issue_id, type, subject, message)
        VALUES (NEW.member_id, NEW.issue_id, 'Return Receipt',
                CONCAT('Book returned: ', v_title),
                CONCAT('Dear ', v_name, ', we have received "', v_title, '" on ',
                       DATE_FORMAT(NEW.return_date, '%d %b %Y'), '. Thank you!'));
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `members`
--

DROP TABLE IF EXISTS `members`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `members` (
  `member_id` int NOT NULL AUTO_INCREMENT,
  `full_name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `member_type` enum('Student','Faculty','Public') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Student',
  `status` enum('Active','Suspended','Expired') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Active',
  `joined_on` date NOT NULL DEFAULT (curdate()),
  `expires_on` date NOT NULL,
  PRIMARY KEY (`member_id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `members`
--

LOCK TABLES `members` WRITE;
/*!40000 ALTER TABLE `members` DISABLE KEYS */;
INSERT INTO `members` VALUES (1,'Aarav Sharma','aarav@example.com','9000000001',NULL,'Student','Active','2026-10-07','2027-08-03'),(2,'Diya Reddy','diya@example.com','9000000002',NULL,'Student','Active','2026-10-07','2027-08-03'),(3,'Rohan Mehta','rohan@example.com','9000000003',NULL,'Faculty','Active','2026-10-07','2027-08-03'),(4,'Sneha Iyer','sneha@example.com','9000000004',NULL,'Public','Active','2026-10-07','2027-04-25'),(5,'Karthik Rao','karthik@example.com','9000000005',NULL,'Student','Active','2026-10-07','2027-08-03'),(6,'Meera Nair','meera@example.com','9000000006',NULL,'Public','Active','2026-10-07','2027-01-15'),(7,'abc','abc@gmail.com','7894561230','','Student','Active','2026-10-07','2027-10-07');
/*!40000 ALTER TABLE `members` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notifications`
--

DROP TABLE IF EXISTS `notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notifications` (
  `notification_id` int NOT NULL AUTO_INCREMENT,
  `member_id` int NOT NULL,
  `issue_id` int DEFAULT NULL,
  `type` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `subject` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` enum('Pending','Sent','Failed') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pending',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `sent_at` datetime DEFAULT NULL,
  `error` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`notification_id`),
  KEY `member_id` (`member_id`),
  KEY `idx_notif_status` (`status`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notifications`
--

LOCK TABLES `notifications` WRITE;
/*!40000 ALTER TABLE `notifications` DISABLE KEYS */;
INSERT INTO `notifications` VALUES (1,1,1,'Issue Confirmation','Book issued: 1984','Dear Aarav Sharma, \"1984\" has been issued to you. Due date: 11 Sep 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(2,2,2,'Issue Confirmation','Book issued: Sapiens','Dear Diya Reddy, \"Sapiens\" has been issued to you. Due date: 21 Sep 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(3,3,3,'Issue Confirmation','Book issued: Clean Code','Dear Rohan Mehta, \"Clean Code\" has been issued to you. Due date: 26 Sep 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(4,2,4,'Issue Confirmation','Book issued: 1984','Dear Diya Reddy, \"1984\" has been issued to you. Due date: 06 Oct 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(5,4,5,'Issue Confirmation','Book issued: Python How to Program','Dear Sneha Iyer, \"Python How to Program\" has been issued to you. Due date: 11 Oct 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(6,5,6,'Issue Confirmation','Book issued: To Kill a Mockingbird','Dear Karthik Rao, \"To Kill a Mockingbird\" has been issued to you. Due date: 21 Sep 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(7,3,7,'Issue Confirmation','Book issued: 1984','Dear Rohan Mehta, \"1984\" has been issued to you. Due date: 16 Oct 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(8,6,8,'Issue Confirmation','Book issued: The Alchemist','Dear Meera Nair, \"The Alchemist\" has been issued to you. Due date: 18 Oct 2026.','Pending','2026-10-07 04:03:24',NULL,NULL),(9,1,1,'Fine Notice','Fine charged: 1984','Dear Aarav Sharma, a fine of 30.00 (Overdue, 6 day(s) late) was charged for \"1984\".','Pending','2026-10-07 04:03:24',NULL,NULL),(10,1,1,'Return Receipt','Book returned: 1984','Dear Aarav Sharma, we have received \"1984\" on 17 Sep 2026. Thank you!','Pending','2026-10-07 04:03:24',NULL,NULL),(11,2,2,'Return Receipt','Book returned: Sapiens','Dear Diya Reddy, we have received \"Sapiens\" on 19 Sep 2026. Thank you!','Pending','2026-10-07 04:03:24',NULL,NULL),(12,3,3,'Return Receipt','Book returned: Clean Code','Dear Rohan Mehta, we have received \"Clean Code\" on 25 Sep 2026. Thank you!','Pending','2026-10-07 04:03:24',NULL,NULL),(13,2,4,'Return Receipt','Book returned: 1984','Dear Diya Reddy, we have received \"1984\" on 02 Oct 2026. Thank you!','Pending','2026-10-07 04:03:24',NULL,NULL),(14,5,6,'Overdue Notice','Overdue: To Kill a Mockingbird','Dear Karthik Rao, \"To Kill a Mockingbird\" was due on 21 Sep 2026. Fine so far: 80.00. Please return it soon.','Pending','2026-10-07 04:03:24',NULL,NULL),(15,1,NULL,'Fine Update','Fine waived','Your fine of 30.00 has been marked as waived.','Pending','2026-10-07 04:08:53',NULL,NULL);
/*!40000 ALTER TABLE `notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `publishers`
--

DROP TABLE IF EXISTS `publishers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `publishers` (
  `publisher_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `city` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`publisher_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `publishers`
--

LOCK TABLES `publishers` WRITE;
/*!40000 ALTER TABLE `publishers` DISABLE KEYS */;
INSERT INTO `publishers` VALUES (1,'Penguin Random House','New York','info@prh.example'),(2,'HarperCollins','London','contact@harper.example'),(3,'O\'Reilly Media','Sebastopol','hello@oreilly.example'),(4,'Pearson','London','support@pearson.example');
/*!40000 ALTER TABLE `publishers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservations` (
  `reservation_id` int NOT NULL AUTO_INCREMENT,
  `book_id` int NOT NULL,
  `member_id` int NOT NULL,
  `reserved_on` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `status` enum('Pending','Ready','Fulfilled','Cancelled','Expired') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'Pending',
  `copy_id` int DEFAULT NULL,
  `ready_until` datetime DEFAULT NULL,
  PRIMARY KEY (`reservation_id`),
  KEY `member_id` (`member_id`),
  KEY `copy_id` (`copy_id`),
  KEY `idx_res_book_status` (`book_id`,`status`),
  CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`book_id`) REFERENCES `books` (`book_id`),
  CONSTRAINT `reservations_ibfk_2` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`),
  CONSTRAINT `reservations_ibfk_3` FOREIGN KEY (`copy_id`) REFERENCES `book_copies` (`copy_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservations`
--

LOCK TABLES `reservations` WRITE;
/*!40000 ALTER TABLE `reservations` DISABLE KEYS */;
/*!40000 ALTER TABLE `reservations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `settings`
--

DROP TABLE IF EXISTS `settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `settings` (
  `setting_key` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `setting_value` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`setting_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `settings`
--

LOCK TABLES `settings` WRITE;
/*!40000 ALTER TABLE `settings` DISABLE KEYS */;
INSERT INTO `settings` VALUES ('fine_block_limit','100.00'),('fine_per_day','5.00'),('loan_days','14'),('max_loans','5'),('reservation_hold_days','3');
/*!40000 ALTER TABLE `settings` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` enum('librarian','student') COLLATE utf8mb4_unicode_ci NOT NULL,
  `member_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  KEY `member_id` (`member_id`),
  KEY `idx_users_username` (`username`),
  KEY `idx_users_role` (`role`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`member_id`) REFERENCES `members` (`member_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'librarian','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','librarian',NULL,'2026-10-07 04:20:26'),(2,'admin','240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9','librarian',NULL,'2026-10-07 04:20:26'),(3,'aarav','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student',1,'2026-10-07 04:20:26'),(4,'diya','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student',2,'2026-10-07 04:20:26'),(5,'rohan','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student',3,'2026-10-07 04:20:26'),(6,'sneha','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student',4,'2026-10-07 04:20:26'),(7,'karthik','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student',5,'2026-10-07 04:20:26'),(8,'meera','703b0a3d6ad75b649a28adde7d83c6251da457549263bc7ff45ec709b0a8448b','student',6,'2026-10-07 04:20:26'),(9,'abc','9462db389127710c1c52e4d6ebecc17f9163730d14b86c3b87050eca286dee66','student',7,'2026-10-07 04:26:05');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `v_active_loans`
--

DROP TABLE IF EXISTS `v_active_loans`;
/*!50001 DROP VIEW IF EXISTS `v_active_loans`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_active_loans` AS SELECT 
 1 AS `issue_id`,
 1 AS `member_id`,
 1 AS `full_name`,
 1 AS `title`,
 1 AS `barcode`,
 1 AS `issue_date`,
 1 AS `due_date`,
 1 AS `days_overdue`,
 1 AS `accrued_fine`,
 1 AS `is_overdue`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_catalog`
--

DROP TABLE IF EXISTS `v_catalog`;
/*!50001 DROP VIEW IF EXISTS `v_catalog`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_catalog` AS SELECT 
 1 AS `book_id`,
 1 AS `isbn`,
 1 AS `title`,
 1 AS `authors`,
 1 AS `publisher`,
 1 AS `category`,
 1 AS `publication_year`,
 1 AS `price`,
 1 AS `total_copies`,
 1 AS `available_copies`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_circulation_history`
--

DROP TABLE IF EXISTS `v_circulation_history`;
/*!50001 DROP VIEW IF EXISTS `v_circulation_history`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_circulation_history` AS SELECT 
 1 AS `issue_id`,
 1 AS `member_id`,
 1 AS `full_name`,
 1 AS `title`,
 1 AS `barcode`,
 1 AS `issue_date`,
 1 AS `due_date`,
 1 AS `return_date`,
 1 AS `status`,
 1 AS `return_condition`,
 1 AS `fine_amount`,
 1 AS `fine_status`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_popular_books`
--

DROP TABLE IF EXISTS `v_popular_books`;
/*!50001 DROP VIEW IF EXISTS `v_popular_books`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_popular_books` AS SELECT 
 1 AS `book_id`,
 1 AS `title`,
 1 AS `category`,
 1 AS `times_borrowed`,
 1 AS `unique_members`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping routines for database 'digital_library'
--
/*!50003 DROP FUNCTION IF EXISTS `fn_available_copies` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_available_copies`(p_book INT) RETURNS int
    READS SQL DATA
BEGIN
    DECLARE n INT;
    SELECT COUNT(*) INTO n FROM book_copies WHERE book_id = p_book AND status = 'Available';
    RETURN n;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_calc_fine` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_calc_fine`(p_due DATE, p_returned DATE) RETURNS decimal(10,2)
    READS SQL DATA
BEGIN
    RETURN GREATEST(DATEDIFF(p_returned, p_due), 0) * fn_setting('fine_per_day');
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_member_active_loans` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_member_active_loans`(p_member INT) RETURNS int
    READS SQL DATA
BEGIN
    DECLARE n INT;
    SELECT COUNT(*) INTO n FROM issues WHERE member_id = p_member AND return_date IS NULL;
    RETURN n;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_member_unpaid_fines` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_member_unpaid_fines`(p_member INT) RETURNS decimal(10,2)
    READS SQL DATA
BEGIN
    DECLARE total DECIMAL(10,2);
    SELECT IFNULL(SUM(amount), 0) INTO total FROM fines WHERE member_id = p_member AND status = 'Unpaid';
    RETURN total;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP FUNCTION IF EXISTS `fn_setting` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` FUNCTION `fn_setting`(p_key VARCHAR(50)) RETURNS decimal(10,2)
    READS SQL DATA
BEGIN
    DECLARE v DECIMAL(10,2);
    SELECT CAST(setting_value AS DECIMAL(10,2)) INTO v FROM settings WHERE setting_key = p_key;
    RETURN IFNULL(v, 0);
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_cancel_reservation` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_cancel_reservation`(IN p_res INT)
BEGIN
    DECLARE v_status VARCHAR(10);
    DECLARE v_copy   INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT status, copy_id INTO v_status, v_copy
      FROM reservations WHERE reservation_id = p_res FOR UPDATE;

    IF v_status IS NULL OR v_status NOT IN ('Pending', 'Ready') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation not found or no longer active';
    END IF;

    UPDATE reservations SET status = 'Cancelled' WHERE reservation_id = p_res;
    IF v_status = 'Ready' THEN
        CALL sp_release_copy(v_copy);
    END IF;

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_daily_maintenance` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_daily_maintenance`()
BEGIN
    UPDATE issues SET status = 'Overdue'
     WHERE return_date IS NULL AND status = 'Issued' AND due_date < CURDATE();

    INSERT INTO notifications (member_id, issue_id, type, subject, message)
    SELECT i.member_id, i.issue_id, 'Overdue Notice', CONCAT('Overdue: ', b.title),
           CONCAT('Dear ', m.full_name, ', "', b.title, '" was due on ',
                  DATE_FORMAT(i.due_date, '%d %b %Y'), '. Fine so far: ',
                  fn_calc_fine(i.due_date, CURDATE()), '. Please return it soon.')
      FROM issues i
      JOIN members m     ON m.member_id = i.member_id
      JOIN book_copies c ON c.copy_id = i.copy_id
      JOIN books b       ON b.book_id = c.book_id
     WHERE i.return_date IS NULL AND i.due_date < CURDATE()
       AND NOT EXISTS (SELECT 1 FROM notifications n
                        WHERE n.issue_id = i.issue_id AND n.type = 'Overdue Notice'
                          AND DATE(n.created_at) = CURDATE());

    INSERT INTO notifications (member_id, issue_id, type, subject, message)
    SELECT i.member_id, i.issue_id, 'Due Reminder', CONCAT('Due soon: ', b.title),
           CONCAT('Dear ', m.full_name, ', "', b.title, '" is due on ',
                  DATE_FORMAT(i.due_date, '%d %b %Y'), '.')
      FROM issues i
      JOIN members m     ON m.member_id = i.member_id
      JOIN book_copies c ON c.copy_id = i.copy_id
      JOIN books b       ON b.book_id = c.book_id
     WHERE i.return_date IS NULL AND i.due_date = DATE_ADD(CURDATE(), INTERVAL 2 DAY)
       AND NOT EXISTS (SELECT 1 FROM notifications n
                        WHERE n.issue_id = i.issue_id AND n.type = 'Due Reminder');

    UPDATE members SET status = 'Expired' WHERE status = 'Active' AND expires_on < CURDATE();

    CALL sp_expire_reservations();
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_expire_reservations` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_expire_reservations`()
BEGIN
    DECLARE done     INT DEFAULT 0;
    DECLARE v_res    INT;
    DECLARE v_copy   INT;
    DECLARE v_member INT;
    DECLARE cur CURSOR FOR
        SELECT reservation_id, copy_id, member_id FROM reservations
         WHERE status = 'Ready' AND ready_until < NOW();
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = 1;

    OPEN cur;
    read_loop: LOOP
        FETCH cur INTO v_res, v_copy, v_member;
        IF done = 1 THEN
            LEAVE read_loop;
        END IF;
        UPDATE reservations SET status = 'Expired' WHERE reservation_id = v_res;
        INSERT INTO notifications (member_id, type, subject, message)
        VALUES (v_member, 'Reservation Expired', 'Your reservation has expired',
                'The hold period for your reserved book has ended and the copy was released.');
        CALL sp_release_copy(v_copy);
    END LOOP;
    CLOSE cur;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_issue_book` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_issue_book`(IN p_member INT, IN p_copy INT)
BEGIN
    DECLARE v_status VARCHAR(20);
    DECLARE v_book   INT;
    DECLARE v_res    INT;
    DECLARE v_issue  INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT status, book_id INTO v_status, v_book
      FROM book_copies WHERE copy_id = p_copy FOR UPDATE;

    IF v_status IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book copy not found';
    END IF;

    IF EXISTS (SELECT 1 FROM issues i JOIN book_copies c ON c.copy_id = i.copy_id
                WHERE i.member_id = p_member AND c.book_id = v_book AND i.return_date IS NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member already has a copy of this book';
    END IF;

    IF v_status = 'Reserved' THEN
        SELECT MIN(reservation_id) INTO v_res FROM reservations
         WHERE copy_id = p_copy AND member_id = p_member AND status = 'Ready' AND ready_until >= NOW();
        IF v_res IS NULL THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This copy is being held for another member';
        END IF;
        UPDATE reservations SET status = 'Fulfilled' WHERE reservation_id = v_res;
    ELSEIF v_status <> 'Available' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'This copy is not available for issue';
    END IF;

    INSERT INTO issues (copy_id, member_id, issue_date, due_date)
    VALUES (p_copy, p_member, CURDATE(), DATE_ADD(CURDATE(), INTERVAL fn_setting('loan_days') DAY));
    SET v_issue = LAST_INSERT_ID();

    -- a pending reservation of the same book by this member is now satisfied
    UPDATE reservations SET status = 'Fulfilled'
     WHERE member_id = p_member AND book_id = v_book AND status = 'Pending';

    COMMIT;
    SELECT v_issue AS issue_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_release_copy` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_release_copy`(IN p_copy INT)
BEGIN
    DECLARE v_book   INT;
    DECLARE v_title  VARCHAR(200);
    DECLARE v_res    INT;
    DECLARE v_member INT;
    DECLARE v_until  DATETIME;

    SELECT c.book_id, b.title INTO v_book, v_title
      FROM book_copies c JOIN books b ON b.book_id = c.book_id
     WHERE c.copy_id = p_copy;

    SELECT MIN(reservation_id) INTO v_res
      FROM reservations WHERE book_id = v_book AND status = 'Pending';

    IF v_res IS NULL THEN
        UPDATE book_copies SET status = 'Available' WHERE copy_id = p_copy;
    ELSE
        SET v_until = DATE_ADD(NOW(), INTERVAL fn_setting('reservation_hold_days') DAY);
        UPDATE reservations SET status = 'Ready', copy_id = p_copy, ready_until = v_until
         WHERE reservation_id = v_res;
        UPDATE book_copies SET status = 'Reserved' WHERE copy_id = p_copy;
        SELECT member_id INTO v_member FROM reservations WHERE reservation_id = v_res;
        INSERT INTO notifications (member_id, type, subject, message)
        VALUES (v_member, 'Reservation Ready',
                CONCAT('Your reserved book is ready: ', v_title),
                CONCAT('"', v_title, '" is now held for you until ',
                       DATE_FORMAT(v_until, '%d %b %Y %H:%i'), '. Please collect it from the circulation desk.'));
    END IF;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_reserve_book` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_reserve_book`(IN p_member INT, IN p_book INT)
BEGIN
    DECLARE v_title VARCHAR(200);
    DECLARE v_name  VARCHAR(120);
    DECLARE v_id    INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    SELECT title INTO v_title FROM books WHERE book_id = p_book;
    SELECT full_name INTO v_name FROM members
     WHERE member_id = p_member AND status = 'Active' AND expires_on >= CURDATE();

    IF v_name IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member is not active or membership has expired';
    END IF;
    IF v_title IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book not found';
    END IF;
    IF fn_available_copies(p_book) > 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'A copy is available right now - issue it instead of reserving';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM book_copies WHERE book_id = p_book AND status IN ('Issued', 'Reserved')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No circulating copy exists to wait for (all lost or damaged)';
    END IF;
    IF EXISTS (SELECT 1 FROM reservations
                WHERE book_id = p_book AND member_id = p_member AND status IN ('Pending', 'Ready')) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member already has an active reservation for this book';
    END IF;
    IF EXISTS (SELECT 1 FROM issues i JOIN book_copies c ON c.copy_id = i.copy_id
                WHERE i.member_id = p_member AND c.book_id = p_book AND i.return_date IS NULL) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Member already has this book on loan';
    END IF;

    INSERT INTO reservations (book_id, member_id) VALUES (p_book, p_member);
    SET v_id = LAST_INSERT_ID();

    INSERT INTO notifications (member_id, type, subject, message)
    VALUES (p_member, 'Reservation Placed',
            CONCAT('Reservation placed: ', v_title),
            CONCAT('Dear ', v_name, ', you are in the queue for "', v_title,
                   '". We will email you when a copy is ready.'));

    COMMIT;
    SELECT v_id AS reservation_id;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_return_book` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_return_book`(IN p_issue INT, IN p_condition VARCHAR(10))
BEGIN
    DECLARE v_found INT;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_condition NOT IN ('Good', 'Damaged', 'Lost') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Condition must be Good, Damaged or Lost';
    END IF;

    START TRANSACTION;

    SELECT issue_id INTO v_found FROM issues
     WHERE issue_id = p_issue AND return_date IS NULL FOR UPDATE;
    IF v_found IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Issue record not found or already returned';
    END IF;

    UPDATE issues SET return_date = CURDATE(), return_condition = p_condition
     WHERE issue_id = p_issue;

    COMMIT;
    SELECT i.issue_id, i.return_date, IFNULL(f.amount, 0) AS fine_amount, f.reason AS fine_reason
      FROM issues i LEFT JOIN fines f ON f.issue_id = i.issue_id
     WHERE i.issue_id = p_issue;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!50003 DROP PROCEDURE IF EXISTS `sp_settle_fine` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_settle_fine`(IN p_fine INT, IN p_action VARCHAR(10))
BEGIN
    DECLARE v_member INT;
    DECLARE v_amount DECIMAL(10,2);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    IF p_action NOT IN ('Paid', 'Waived') THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Action must be Paid or Waived';
    END IF;

    START TRANSACTION;

    SELECT member_id, amount INTO v_member, v_amount
      FROM fines WHERE fine_id = p_fine AND status = 'Unpaid' FOR UPDATE;
    IF v_member IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Fine not found or already settled';
    END IF;

    UPDATE fines SET status = p_action, paid_on = NOW() WHERE fine_id = p_fine;

    INSERT INTO notifications (member_id, type, subject, message)
    VALUES (v_member, 'Fine Update', CONCAT('Fine ', LOWER(p_action)),
            CONCAT('Your fine of ', v_amount, ' has been marked as ', LOWER(p_action), '.'));

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Current Database: `digital_library`
--

USE `digital_library`;

--
-- Final view structure for view `v_active_loans`
--

/*!50001 DROP VIEW IF EXISTS `v_active_loans`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_active_loans` AS select `i`.`issue_id` AS `issue_id`,`m`.`member_id` AS `member_id`,`m`.`full_name` AS `full_name`,`b`.`title` AS `title`,`c`.`barcode` AS `barcode`,`i`.`issue_date` AS `issue_date`,`i`.`due_date` AS `due_date`,greatest((to_days(curdate()) - to_days(`i`.`due_date`)),0) AS `days_overdue`,`fn_calc_fine`(`i`.`due_date`,curdate()) AS `accrued_fine`,(`i`.`due_date` < curdate()) AS `is_overdue` from (((`issues` `i` join `members` `m` on((`m`.`member_id` = `i`.`member_id`))) join `book_copies` `c` on((`c`.`copy_id` = `i`.`copy_id`))) join `books` `b` on((`b`.`book_id` = `c`.`book_id`))) where (`i`.`return_date` is null) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_catalog`
--

/*!50001 DROP VIEW IF EXISTS `v_catalog`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_catalog` AS select `b`.`book_id` AS `book_id`,`b`.`isbn` AS `isbn`,`b`.`title` AS `title`,ifnull(group_concat(distinct `a`.`name` order by `a`.`name` ASC separator ', '),'-') AS `authors`,`p`.`name` AS `publisher`,`c`.`name` AS `category`,`b`.`publication_year` AS `publication_year`,`b`.`price` AS `price`,(select count(0) from `book_copies` `x` where (`x`.`book_id` = `b`.`book_id`)) AS `total_copies`,`fn_available_copies`(`b`.`book_id`) AS `available_copies` from ((((`books` `b` join `publishers` `p` on((`p`.`publisher_id` = `b`.`publisher_id`))) join `categories` `c` on((`c`.`category_id` = `b`.`category_id`))) left join `book_authors` `ba` on((`ba`.`book_id` = `b`.`book_id`))) left join `authors` `a` on((`a`.`author_id` = `ba`.`author_id`))) group by `b`.`book_id`,`b`.`isbn`,`b`.`title`,`p`.`name`,`c`.`name`,`b`.`publication_year`,`b`.`price` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_circulation_history`
--

/*!50001 DROP VIEW IF EXISTS `v_circulation_history`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_circulation_history` AS select `i`.`issue_id` AS `issue_id`,`m`.`member_id` AS `member_id`,`m`.`full_name` AS `full_name`,`b`.`title` AS `title`,`c`.`barcode` AS `barcode`,`i`.`issue_date` AS `issue_date`,`i`.`due_date` AS `due_date`,`i`.`return_date` AS `return_date`,`i`.`status` AS `status`,`i`.`return_condition` AS `return_condition`,ifnull(`f`.`amount`,0) AS `fine_amount`,`f`.`status` AS `fine_status` from ((((`issues` `i` join `members` `m` on((`m`.`member_id` = `i`.`member_id`))) join `book_copies` `c` on((`c`.`copy_id` = `i`.`copy_id`))) join `books` `b` on((`b`.`book_id` = `c`.`book_id`))) left join `fines` `f` on((`f`.`issue_id` = `i`.`issue_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_popular_books`
--

/*!50001 DROP VIEW IF EXISTS `v_popular_books`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_popular_books` AS select `b`.`book_id` AS `book_id`,`b`.`title` AS `title`,`cat`.`name` AS `category`,count(`i`.`issue_id`) AS `times_borrowed`,count(distinct `i`.`member_id`) AS `unique_members` from (((`books` `b` join `categories` `cat` on((`cat`.`category_id` = `b`.`category_id`))) left join `book_copies` `c` on((`c`.`book_id` = `b`.`book_id`))) left join `issues` `i` on((`i`.`copy_id` = `c`.`copy_id`))) group by `b`.`book_id`,`b`.`title`,`cat`.`name` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-08 23:28:19

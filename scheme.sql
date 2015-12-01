-- MySQL Workbench Synchronization
-- Generated: 2015-11-30 23:52
-- Model: New Model
-- Version: 1.0
-- Project: Name of the project
-- Author: stalker

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `forums` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;

CREATE TABLE IF NOT EXISTS `forums`.`User` (
  `idUser` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `username` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `about` MEDIUMTEXT NULL DEFAULT NULL COMMENT '',
  `name` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `email` CHAR(45) NOT NULL COMMENT '',
  `isAnonymous` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  PRIMARY KEY (`idUser`)  COMMENT '',
  UNIQUE INDEX `email_UNIQUE` (`email` ASC)  COMMENT '')
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `forums`.`Forum` (
  `idForum` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `name` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `short_name` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `user` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `posts` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  PRIMARY KEY (`idForum`)  COMMENT '',
  UNIQUE INDEX `name_UNIQUE` (`name` ASC)  COMMENT '',
  UNIQUE INDEX `shortName_UNIQUE` (`short_name` ASC)  COMMENT '',
  INDEX `fk_Forum_idx` (`user` ASC)  COMMENT '',
  CONSTRAINT `fk_Forum`
    FOREIGN KEY (`user`)
    REFERENCES `forums`.`User` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `forums`.`Thread` (
  `idThread` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `forum` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `user` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `title` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `slug` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `message` TEXT NULL DEFAULT NULL COMMENT '',
  `dateThread` DATETIME NULL DEFAULT NULL COMMENT '',
  `isClosed` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `isDeleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `likes` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  `dislikes` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  `points` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  `posts` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  PRIMARY KEY (`idThread`)  COMMENT '',
  INDEX `fk_Thread_1_idx` (`user` ASC)  COMMENT '',
  INDEX `fk_Thread_2_idx` (`forum` ASC)  COMMENT '',
  CONSTRAINT `fk_Thread_1`
    FOREIGN KEY (`user`)
    REFERENCES `forums`.`User` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Thread_2`
    FOREIGN KEY (`forum`)
    REFERENCES `forums`.`Forum` (`short_name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `forums`.`Post` (
  `idPost` INT(11) NOT NULL AUTO_INCREMENT COMMENT '',
  `forum` CHAR(45) NOT NULL COMMENT '',
  `idThread` INT(11) NULL DEFAULT NULL COMMENT '',
  `user` CHAR(45) NULL DEFAULT NULL COMMENT '',
  `parent` INT(11) NULL DEFAULT NULL COMMENT '',
  `datePost` DATETIME NULL DEFAULT NULL COMMENT '',
  `message` MEDIUMTEXT NULL DEFAULT NULL COMMENT '',
  `isEdited` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `isDeleted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `isSpam` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `isHighlighted` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `isApproved` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `likes` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  `dislikes` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  `points` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  `path` VARCHAR(345) NOT NULL COMMENT '',
  `isRoot` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '',
  `level` INT(11) NOT NULL DEFAULT 0 COMMENT '',
  PRIMARY KEY (`idPost`)  COMMENT '',
  INDEX `fk_Post_3_idx` (`parent` ASC)  COMMENT '',
  INDEX `fk_Post_1_idx` (`user` ASC)  COMMENT '',
  INDEX `fk_Post_2_idx` (`idThread` ASC)  COMMENT '',
  INDEX `fk_Post_4_idx` (`forum` ASC)  COMMENT '',
  CONSTRAINT `fk_Post_1`
    FOREIGN KEY (`user`)
    REFERENCES `forums`.`User` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Post_2`
    FOREIGN KEY (`idThread`)
    REFERENCES `forums`.`Thread` (`idThread`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Post_3`
    FOREIGN KEY (`parent`)
    REFERENCES `forums`.`Post` (`idPost`)
    ON DELETE CASCADE
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Post_4`
    FOREIGN KEY (`forum`)
    REFERENCES `forums`.`Forum` (`short_name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `forums`.`Followers` (
  `user` CHAR(45) NOT NULL COMMENT 'тот на кого подписаны',
  `follower` CHAR(45) NOT NULL COMMENT 'подписчики ',
  PRIMARY KEY (`user`, `follower`)  COMMENT '',
  INDEX `fk_Followers_2_idx` (`follower` ASC)  COMMENT '',
  CONSTRAINT `fk_Followers_1`
    FOREIGN KEY (`user`)
    REFERENCES `forums`.`User` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Followers_2`
    FOREIGN KEY (`follower`)
    REFERENCES `forums`.`User` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;

CREATE TABLE IF NOT EXISTS `forums`.`Subscriptions` (
  `user` CHAR(45) NOT NULL COMMENT '',
  `idThread` INT(11) NOT NULL COMMENT '',
  PRIMARY KEY (`idThread`, `user`)  COMMENT '',
  INDEX `fk_Subscriptions_2_idx` (`idThread` ASC)  COMMENT '',
  CONSTRAINT `fk_Subscriptions_1`
    FOREIGN KEY (`user`)
    REFERENCES `forums`.`User` (`email`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Subscriptions_2`
    FOREIGN KEY (`idThread`)
    REFERENCES `forums`.`Thread` (`idThread`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

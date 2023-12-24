-- Создяём таблицу с пользователями
CREATE TABLE `users` (
	`id` CHAR(19) NOT NULL,
	`username` CHAR(30) NOT NULL,
	`password` CHAR(64) NOT NULL,
	`birthday` DATE DEFAULT NULL,
	`uuid` CHAR(36) UNIQUE DEFAULT NULL,
	`accessToken` CHAR(32) DEFAULT NULL,
	`serverID` VARCHAR(41) DEFAULT NULL,
	`hwidId` BIGINT DEFAULT NULL,
	UNIQUE KEY `user` (`username`),
	UNIQUE KEY `uuid` (`uuid`),
	KEY `id` (`id`) USING BTREE,
	KEY `users_hwidfk` (`hwidId`),
) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB;

-- Создяём таблицу с информацией пользователей в магазине
CREATE TABLE `store` (
	`id` CHAR(19) NULL DEFAULT NULL,
	`money` MEDIUMINT(30) NULL DEFAULT '0',
	`invoice_id` CHAR(36) NULL DEFAULT NULL,
	`data_trial` DATE NULL DEFAULT NULL,
	KEY `Did` (`id`) USING BTREE,
	CONSTRAINT `Did` FOREIGN KEY (`id`) REFERENCES `users` (`id`)
) COLLATE='utf8mb4_general_ci' ENGINE=InnoDB;

-- Создяём таблицу с промокодамии
CREATE TABLE `promo` (
  `id` smallint(6) NOT NULL AUTO_INCREMENT,
  `code` char(50) DEFAULT NULL,
  `use` smallint(6) NOT NULL DEFAULT 0,
  `enabled` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Создаёт триггер на генерацию UUID для новых пользователей
DELIMITER //
CREATE TRIGGER setUUID BEFORE INSERT ON users
FOR EACH ROW BEGIN
IF NEW.uuid IS NULL THEN
SET NEW.uuid = UUID();
END IF;
END; //
DELIMITER ;

-- Генерирует UUID для уже существующих пользователей
UPDATE users SET uuid=(SELECT UUID()) WHERE uuid IS NULL;

-- Создяём таблицу с информацией про железа пользователей
CREATE TABLE `hwids` (
	`id` bigint(20) NOT NULL,
	`publickey` blob,
	`hwDiskId` varchar(255) DEFAULT NULL,
	`baseboardSerialNumber` varchar(255) DEFAULT NULL,
	`graphicCard` varchar(255) DEFAULT NULL,
	`displayId` blob,
	`bitness` int(11) DEFAULT NULL,
	`totalMemory` bigint(20) DEFAULT NULL,
	`logicalProcessors` int(11) DEFAULT NULL,
	`physicalProcessors` int(11) DEFAULT NULL,
	`processorMaxFreq` bigint(11) DEFAULT NULL,
	`battery` tinyint(1) NOT NULL DEFAULT "0",
	`banned` tinyint(1) NOT NULL DEFAULT "0"
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
ALTER TABLE `hwids`
ADD PRIMARY KEY (`id`),
ADD UNIQUE KEY `publickey` (`publickey`(255));
ALTER TABLE `hwids`
MODIFY `id` bigint(20) NOT NULL AUTO_INCREMENT;

ALTER TABLE `users`
ADD CONSTRAINT `users_hwidfk` FOREIGN KEY (`hwidId`) REFERENCES `hwids` (`id`);

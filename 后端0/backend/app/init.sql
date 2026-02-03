-- 运行以下指令创建数据库和表
-- mysql -u root -p < init.sql 
-- 数据库名称：scut_helper
CREATE DATABASE IF NOT EXISTS scut_helper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE scut_helper;
CREATE TABLE IF NOT EXISTS users (
    user_id      CHAR(36)     NOT NULL PRIMARY KEY,
    username     VARCHAR(50)  NOT NULL,
    account_name VARCHAR(20)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


ALTER TABLE scut_helper.users
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;
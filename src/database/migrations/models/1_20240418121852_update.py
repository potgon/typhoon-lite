from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `failedqueue` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `asset_id` INT NOT NULL,
    `model_type_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    CONSTRAINT `fk_failedqu_asset_79e3c3bd` FOREIGN KEY (`asset_id`) REFERENCES `asset` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_failedqu_modeltyp_cc1c03f2` FOREIGN KEY (`model_type_id`) REFERENCES `modeltype` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_failedqu_user_a979329c` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
        ALTER TABLE `queue` DROP COLUMN `failed_fetch`;
        ALTER TABLE `queue` DROP COLUMN `failed_fetch_date`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `queue` ADD `failed_fetch` BOOL NOT NULL  DEFAULT 0;
        ALTER TABLE `queue` ADD `failed_fetch_date` DATETIME(6) NOT NULL;
        DROP TABLE IF EXISTS `failedqueue`;"""

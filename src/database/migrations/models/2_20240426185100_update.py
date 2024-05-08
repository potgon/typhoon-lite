from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `modeltype` MODIFY COLUMN `default_model_architecture` JSON NOT NULL;
        ALTER TABLE `tempmodel` MODIFY COLUMN `model_architecture` JSON NOT NULL;
        ALTER TABLE `trainedmodel` MODIFY COLUMN `model_architecture` JSON NOT NULL;
        ALTER TABLE `user` ADD `username` VARCHAR(50) NOT NULL UNIQUE;
        ALTER TABLE `user` ADD UNIQUE INDEX `uid_user_usernam_9987ab` (`username`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `user` DROP INDEX `idx_user_usernam_9987ab`;
        ALTER TABLE `user` DROP COLUMN `username`;
        ALTER TABLE `modeltype` MODIFY COLUMN `default_model_architecture` LONGTEXT NOT NULL;
        ALTER TABLE `tempmodel` MODIFY COLUMN `model_architecture` LONGTEXT NOT NULL;
        ALTER TABLE `trainedmodel` MODIFY COLUMN `model_architecture` LONGTEXT NOT NULL;"""

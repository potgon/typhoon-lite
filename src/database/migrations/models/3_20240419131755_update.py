from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `modeltype` MODIFY COLUMN `default_model_architecture` JSON NOT NULL;
        ALTER TABLE `modeltype` MODIFY COLUMN `description` LONGTEXT NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `modeltype` MODIFY COLUMN `default_model_architecture` LONGTEXT NOT NULL;
        ALTER TABLE `modeltype` MODIFY COLUMN `description` JSON NOT NULL;"""

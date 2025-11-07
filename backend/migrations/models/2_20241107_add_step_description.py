from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 添加步骤描述字段到步骤执行记录表
        ALTER TABLE `test_ui_case_step_execution_records` ADD COLUMN `description` TEXT NULL COMMENT '步骤描述';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 回滚：删除步骤描述字段
        ALTER TABLE `test_ui_case_step_execution_records` DROP COLUMN `description`;
        """

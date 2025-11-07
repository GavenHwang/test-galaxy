from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 添加日志文件路径字段到测试任务表
        ALTER TABLE `test_ui_tasks` ADD COLUMN `log_file_path` VARCHAR(500) NULL COMMENT '日志文件路径';
        """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 回滚：删除日志文件路径字段
        ALTER TABLE `test_ui_tasks` DROP COLUMN `log_file_path`;
        """
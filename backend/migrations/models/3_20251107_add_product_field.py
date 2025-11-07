"""
数据库迁移脚本：添加产品字段和产品主数据表
创建时间：2025-11-07
"""
from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 步骤一：创建产品主数据表
        CREATE TABLE IF NOT EXISTS `test_products` (
            `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
            `name` VARCHAR(100) NOT NULL UNIQUE COMMENT '产品名称',
            `code` VARCHAR(50) UNIQUE COMMENT '产品编码',
            `description` TEXT COMMENT '产品描述',
            `status` VARCHAR(20) NOT NULL DEFAULT '启用' COMMENT '状态',
            `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序序号',
            `created_by` VARCHAR(50) NOT NULL COMMENT '创建人',
            `created_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT '创建时间',
            `updated_time` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT '更新时间',
            INDEX `idx_test_products_status` (`status`),
            INDEX `idx_test_products_sort_order` (`sort_order`)
        ) COMMENT='产品主数据表';
        
        -- 步骤二：插入初始产品数据
        INSERT INTO `test_products` (`name`, `code`, `status`, `sort_order`, `created_by`) VALUES
        ('平台端', 'PLATFORM', '启用', 1, 'system'),
        ('集群端', 'CLUSTER', '启用', 2, 'system'),
        ('通用市场', 'COMMON_MARKET', '启用', 3, 'system');
        
        -- 步骤三：为各业务表添加product字段
        
        -- 为页面元素表添加product字段
        ALTER TABLE `test_ui_elements` 
        ADD COLUMN `product` VARCHAR(100) NOT NULL DEFAULT '平台端' COMMENT '所属产品' AFTER `module`;
        
        -- 为测试用例表添加product字段
        ALTER TABLE `test_ui_cases` 
        ADD COLUMN `product` VARCHAR(100) NOT NULL DEFAULT '平台端' COMMENT '所属产品' AFTER `module`;
        
        -- 为测试套件表添加product字段
        ALTER TABLE `test_ui_case_suites` 
        ADD COLUMN `product` VARCHAR(100) NOT NULL DEFAULT '平台端' COMMENT '所属产品' AFTER `description`;
        
        -- 为测试单表添加product字段
        ALTER TABLE `test_ui_tasks` 
        ADD COLUMN `product` VARCHAR(100) NOT NULL DEFAULT '平台端' COMMENT '所属产品' AFTER `description`;
        
        -- 为测试报告表添加product字段
        ALTER TABLE `test_ui_reports` 
        ADD COLUMN `product` VARCHAR(100) NOT NULL DEFAULT '平台端' COMMENT '所属产品' AFTER `test_task_id`;
        
        -- 步骤四：为product字段添加索引
        ALTER TABLE `test_ui_elements` ADD INDEX `idx_test_ui_elements_product` (`product`);
        ALTER TABLE `test_ui_cases` ADD INDEX `idx_test_ui_cases_product` (`product`);
        ALTER TABLE `test_ui_case_suites` ADD INDEX `idx_test_ui_case_suites_product` (`product`);
        ALTER TABLE `test_ui_tasks` ADD INDEX `idx_test_ui_tasks_product` (`product`);
        ALTER TABLE `test_ui_reports` ADD INDEX `idx_test_ui_reports_product` (`product`);
    """


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        -- 回滚操作：删除product字段和产品表
        
        -- 删除索引
        ALTER TABLE `test_ui_elements` DROP INDEX `idx_test_ui_elements_product`;
        ALTER TABLE `test_ui_cases` DROP INDEX `idx_test_ui_cases_product`;
        ALTER TABLE `test_ui_case_suites` DROP INDEX `idx_test_ui_case_suites_product`;
        ALTER TABLE `test_ui_tasks` DROP INDEX `idx_test_ui_tasks_product`;
        ALTER TABLE `test_ui_reports` DROP INDEX `idx_test_ui_reports_product`;
        
        -- 删除product字段
        ALTER TABLE `test_ui_elements` DROP COLUMN `product`;
        ALTER TABLE `test_ui_cases` DROP COLUMN `product`;
        ALTER TABLE `test_ui_case_suites` DROP COLUMN `product`;
        ALTER TABLE `test_ui_tasks` DROP COLUMN `product`;
        ALTER TABLE `test_ui_reports` DROP COLUMN `product`;
        
        -- 删除产品主数据表
        DROP TABLE IF EXISTS `test_products`;
    """

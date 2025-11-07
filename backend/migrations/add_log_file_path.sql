-- 添加日志文件路径字段到测试任务表
-- 执行此SQL来修复数据库结构

USE test_galaxy;

-- 添加 log_file_path 字段（VARCHAR类型，用于存储日志文件路径）
ALTER TABLE `test_ui_tasks` 
ADD COLUMN `log_file_path` VARCHAR(500) NULL COMMENT '日志文件路径' 
AFTER `end_time`;

-- 验证字段已添加
DESCRIBE `test_ui_tasks`;
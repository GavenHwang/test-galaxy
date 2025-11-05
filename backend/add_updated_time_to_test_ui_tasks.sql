-- 为 test_ui_tasks 表添加 updated_time 字段
ALTER TABLE test_ui_tasks 
ADD COLUMN updated_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) AFTER created_time;

-- 添加索引
ALTER TABLE test_ui_tasks 
ADD INDEX idx_test_ui_tasks_updated_time (updated_time);

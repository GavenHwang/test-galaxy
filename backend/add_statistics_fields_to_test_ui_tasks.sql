-- 为 test_ui_tasks 表添加统计字段
ALTER TABLE test_ui_tasks 
ADD COLUMN total_cases INT NOT NULL DEFAULT 0 COMMENT '总用例数' AFTER end_time;

ALTER TABLE test_ui_tasks 
ADD COLUMN executed_cases INT NOT NULL DEFAULT 0 COMMENT '已执行用例数' AFTER total_cases;

ALTER TABLE test_ui_tasks 
ADD COLUMN passed_cases INT NOT NULL DEFAULT 0 COMMENT '通过用例数' AFTER executed_cases;

ALTER TABLE test_ui_tasks 
ADD COLUMN failed_cases INT NOT NULL DEFAULT 0 COMMENT '失败用例数' AFTER passed_cases;

ALTER TABLE test_ui_tasks 
ADD COLUMN progress DECIMAL(5,2) NOT NULL DEFAULT 0.00 COMMENT '执行进度' AFTER failed_cases;

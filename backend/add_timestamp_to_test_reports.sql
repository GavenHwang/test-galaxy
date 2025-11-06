-- 为 test_ui_reports 表添加时间字段
ALTER TABLE test_ui_reports 
ADD COLUMN created_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) AFTER report_data;

ALTER TABLE test_ui_reports 
ADD COLUMN updated_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) AFTER created_time;

-- 为 test_ui_case_execution_records 表添加时间字段
ALTER TABLE test_ui_case_execution_records 
ADD COLUMN created_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) AFTER screenshot_path;

ALTER TABLE test_ui_case_execution_records 
ADD COLUMN updated_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) AFTER created_time;

-- 为 test_ui_case_step_execution_records 表添加时间字段
ALTER TABLE test_ui_case_step_execution_records 
ADD COLUMN created_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) AFTER screenshot_path;

ALTER TABLE test_ui_case_step_execution_records 
ADD COLUMN updated_time DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) AFTER created_time;

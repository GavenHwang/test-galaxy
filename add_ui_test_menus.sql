-- 添加 UI 自动化测试菜单项
-- 注意：执行前请先确认数据库中现有的菜单 ID，避免冲突

-- 1. 添加一级菜单：UI测试
INSERT INTO menu (label, path, icon, parent_id, created_time, updated_time)
VALUES ('UI测试', '/ui-test', 'Operation', NULL, NOW(), NOW());

-- 获取刚插入的一级菜单 ID（假设为 @ui_test_id）
SET @ui_test_id = LAST_INSERT_ID();

-- 2. 添加二级菜单：测试用户
INSERT INTO menu (label, path, icon, parent_id, created_time, updated_time)
VALUES ('测试用户', '/ui-test/test-users', 'User', @ui_test_id, NOW(), NOW());

-- 3. 添加二级菜单：页面元素
INSERT INTO menu (label, path, icon, parent_id, created_time, updated_time)
VALUES ('页面元素', '/ui-test/elements', 'Grid', @ui_test_id, NOW(), NOW());

-- 4. 添加二级菜单：测试用例
INSERT INTO menu (label, path, icon, parent_id, created_time, updated_time)
VALUES ('测试用例', '/ui-test/test-cases', 'DocumentCopy', @ui_test_id, NOW(), NOW());

-- 5. 关联菜单到角色（假设角色为 admin，ID 为 1）
-- 获取刚插入的菜单 ID
SET @test_users_id = (SELECT id FROM menu WHERE path = '/ui-test/test-users');
SET @elements_id = (SELECT id FROM menu WHERE path = '/ui-test/elements');
SET @test_cases_id = (SELECT id FROM menu WHERE path = '/ui-test/test-cases');

-- 关联到 admin 角色（假设 admin 角色 ID 为 1）
INSERT INTO role_menu (role_id, menu_id)
VALUES 
    (1, @ui_test_id),
    (1, @test_users_id),
    (1, @elements_id),
    (1, @test_cases_id);

-- 验证插入结果
SELECT m.id, m.label, m.path, m.icon, m.parent_id, p.label as parent_label
FROM menu m
LEFT JOIN menu p ON m.parent_id = p.id
WHERE m.label LIKE '%UI%' OR m.label LIKE '%测试%'
ORDER BY m.parent_id, m.id;

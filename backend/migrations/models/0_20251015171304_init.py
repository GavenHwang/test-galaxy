from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `menu` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '菜单唯一标识',
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `label` VARCHAR(50) NOT NULL  COMMENT '菜单名称（带索引，快速查询）',
    `path` VARCHAR(255)   COMMENT '菜单路由地址（可为空，如按钮无路由）',
    `icon` VARCHAR(100)   COMMENT '菜单图标（支持l图标库类名或SVG路径）',
    `parent_id` INT COMMENT '父菜单（关联自身，支持递归查询）',
    CONSTRAINT `fk_menu_menu_a0892170` FOREIGN KEY (`parent_id`) REFERENCES `menu` (`id`) ON DELETE SET NULL,
    KEY `idx_menu_created_88de55` (`created_time`),
    KEY `idx_menu_updated_474266` (`updated_time`),
    KEY `idx_menu_label_d80735` (`label`)
) CHARACTER SET utf8mb4 COMMENT='菜单模型（支持树形结构 + 角色权限控制）';
CREATE TABLE IF NOT EXISTS `project` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '项目名称',
    `desc` VARCHAR(255)   COMMENT '项目描述',
    KEY `idx_project_created_cefad8` (`created_time`),
    KEY `idx_project_updated_11372b` (`updated_time`)
) CHARACTER SET utf8mb4 COMMENT='项目表';
CREATE TABLE IF NOT EXISTS `component` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '组件名称',
    `path` VARCHAR(255) NOT NULL  COMMENT '组件路径',
    `project_id` INT NOT NULL COMMENT '关联项目（外键）',
    CONSTRAINT `fk_componen_project_41b23582` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
    KEY `idx_component_created_a9f7b5` (`created_time`),
    KEY `idx_component_updated_9d04eb` (`updated_time`)
) CHARACTER SET utf8mb4 COMMENT='组件表';
CREATE TABLE IF NOT EXISTS `role` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色名称',
    `desc` VARCHAR(50) NOT NULL UNIQUE COMMENT '角色描述',
    KEY `idx_role_created_62e059` (`created_time`),
    KEY `idx_role_updated_05f222` (`updated_time`)
) CHARACTER SET utf8mb4 COMMENT='角色模型';
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '用户唯一标识',
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    `_password` VARCHAR(255) NOT NULL  COMMENT '密码哈希值',
    `is_active` BOOL NOT NULL  COMMENT '账号激活状态' DEFAULT 1,
    `is_delete` BOOL NOT NULL  COMMENT '账号是否删除' DEFAULT 0,
    `last_login_time` DATETIME(6)   COMMENT '最后登录时间',
    `role_id` INT NOT NULL COMMENT '关联角色',
    CONSTRAINT `fk_user_role_68c1d370` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    KEY `idx_user_created_ce7cb5` (`created_time`),
    KEY `idx_user_updated_3ef0f3` (`updated_time`),
    KEY `idx_user_usernam_9987ab` (`username`),
    KEY `idx_user_is_acti_83722a` (`is_active`),
    KEY `idx_user_last_lo_9e225c` (`last_login_time`)
) CHARACTER SET utf8mb4 COMMENT='用户模型';
CREATE  INDEX `idx_active_user_login_composite` ON `user` (`is_active`, `last_login_time`);
CREATE  INDEX `idx_username_unique` ON `user` (`username`);
CREATE TABLE IF NOT EXISTS `env` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '环境名称',
    `domain` VARCHAR(255) NOT NULL  COMMENT '环境域名',
    `ac_domain` VARCHAR(255) NOT NULL  COMMENT 'AC环境域名',
    `need_version` BOOL NOT NULL  COMMENT '是否需要获取版本号' DEFAULT 0,
    `desc` VARCHAR(255)   COMMENT '环境描述',
    `components` LONGTEXT NOT NULL  COMMENT '组件信息，多个组件用分号分隔',
    `project_id` INT NOT NULL COMMENT '关联项目（外键）',
    `user_id` INT NOT NULL COMMENT '关联用户（外键）',
    CONSTRAINT `fk_env_project_9112b9f4` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_env_user_8630bfa7` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    KEY `idx_env_created_05fa6d` (`created_time`),
    KEY `idx_env_updated_b8f0a4` (`updated_time`)
) CHARACTER SET utf8mb4 COMMENT='环境表';
CREATE TABLE IF NOT EXISTS `component_version` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `created_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `version` VARCHAR(50) NOT NULL  COMMENT '版本号',
    `flag` INT NOT NULL  COMMENT '版本标志，0表示历史版本，1表示当前版本' DEFAULT 0,
    `component_id` INT NOT NULL COMMENT '关联组件（外键）',
    `env_id` INT NOT NULL COMMENT '关联环境（外键）',
    CONSTRAINT `fk_componen_componen_40b3e2a1` FOREIGN KEY (`component_id`) REFERENCES `component` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_componen_env_6e2c8891` FOREIGN KEY (`env_id`) REFERENCES `env` (`id`) ON DELETE CASCADE,
    KEY `idx_component_v_created_41ddcb` (`created_time`),
    KEY `idx_component_v_updated_c29c2c` (`updated_time`)
) CHARACTER SET utf8mb4 COMMENT='组件版本表';
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `role_menu` (
    `role_id` INT NOT NULL,
    `menu_id` INT NOT NULL,
    FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`menu_id`) REFERENCES `menu` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_role_menu_role_id_90801c` (`role_id`, `menu_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

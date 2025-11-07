import asyncio
from app.log import logger
from aerich import Command
from app.settings.config import settings
from app.models import Role
from app.models import Menu
from typing import Optional
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import AuthMiddleware
from app.models.env import Env
from app.models import User
from app.models.env import Component, Project
from tortoise.exceptions import DoesNotExist
from app.config.component import component_info
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.background_task import fetch_scnet_component_versions

# 定义一个全局调度器实例
scheduler = AsyncIOScheduler()


async def init_db():
    from tortoise import Tortoise
    command = Command(tortoise_config=settings.TORTOISE_ORM)
    try:
        await command.init_db(safe=True)
    except FileExistsError:
        pass
    except Exception as e:
        # 忽略索引重复错误 (1061: Duplicate key name)
        if "Duplicate key name" in str(e):
            logger.warn(f"索引已存在，忽略: {e}")
        else:
            raise

    await command.init()
    # try:
    #     await command.migrate()
    # except AttributeError:
    #     logger.warn("unable to retrieve model history from database, model history will be created from scratch")
    #     shutil.rmtree("migrations")
    #     await command.init_db(safe=True)

    await command.upgrade(run_in_transaction=True)
    
    # 重新初始化 Tortoise ORM 以确保模型数据库连接正确设置
    await Tortoise.init(config=settings.TORTOISE_ORM)


async def upsert_menu_tree(menu_data: list, parent: Optional[Menu] = None):
    for item in menu_data:
        # 提取核心字段并处理空值
        menu_fields = {
            "label": item["label"],
            "path": item["path"],
            "icon": item.get("icon"),
            "parent": parent
        }

        try:
            # 尝试获取现有记录
            menu = await Menu.get(path=item["path"])
            # 更新基础字段（保留已有子菜单关系）
            for key, value in menu_fields.items():
                if value is not None:
                    setattr(menu, key, value)
            await menu.save()
        except DoesNotExist:
            # 创建新记录
            menu = await Menu.create(**menu_fields)

        # 递归处理子菜单
        if "children" in item and item["children"]:
            await upsert_menu_tree(item["children"], parent=menu)


# 初始化调用示例
async def init_menus():
    menu_data = [
        {
            "path": '/home',
            "label": '首页',
            "icon": 'house'
        },
        {
            "path": '/',
            "label": '环境',
            "icon": 'location',
            "children": [
                {
                    "path": '/env/info',
                    "label": '环境信息',
                    "icon": 'setting'
                },
                {
                    "path": '/env/version',
                    "label": '组件版本',
                    "icon": 'setting'
                },
                {
                    "path": '/env/compare',
                    "label": '版本比较',
                    "icon": 'setting'
                }
            ]
        },
        {
            "path": '/ui-test',
            "label": 'UI测试',
            "icon": 'Operation',
            "children": [
                {
                    "path": '/ui-test/test-users',
                    "label": '测试用户',
                    "icon": 'User'
                },
                {
                    "path": '/ui-test/elements',
                    "label": '页面元素',
                    "icon": 'Grid'
                },
                {
                    "path": '/ui-test/test-cases',
                    "label": '测试用例',
                    "icon": 'DocumentCopy'
                },
                {
                    "path": '/ui-test/test-suites',
                    "label": '测试套件',
                    "icon": 'FolderOpened'
                },
                {
                    "path": '/ui-test/test-tasks',
                    "label": '测试单',
                    "icon": 'List'
                },
                {
                    "path": '/ui-test/test-reports',
                    "label": '测试报告',
                    "icon": 'Document'
                }
            ]
        },
        {
            "path": '/system',
            "label": '系统设置',
            "icon": 'Setting',
            "children": [
                {
                    "path": '/system/user',
                    "label": '用户管理',
                    "icon": 'User'
                },
                {
                    "path": '/system/products',
                    "label": '项目管理',
                    "icon": 'Files'
                },
                {
                    "path": '/system/menu-permission',
                    "label": '菜单权限',
                    "icon": 'Lock'
                }
            ]
        }
    ]
    await upsert_menu_tree(menu_data)


async def init_roles():
    """初始化系统角色及菜单权限"""
    # 获取所有菜单项
    all_menus = await Menu.all()
    user_mgmt_menu = await Menu.get(path="/system/user")
    menu_permission_menu = await Menu.get(path="/system/menu-permission")

    # 创建或更新superuser角色
    superuser = await get_or_create_role("superuser", "超级管理员")
    await superuser.menus.clear()
    await superuser.menus.add(*all_menus)  # 赋予所有菜单权限

    # 创建或更新common角色
    common = await get_or_create_role("common", "普通用户")
    await common.menus.clear()
    # 排除用户管理和菜单权限管理权限
    await common.menus.add(
        *[m for m in all_menus if m not in [user_mgmt_menu, menu_permission_menu]]
    )


async def get_or_create_role(name: str, desc: str) -> Role:
    """获取或创建角色（支持幂等操作）"""
    try:
        return await Role.get(name=name)
    except DoesNotExist:
        return await Role.create(name=name, desc=desc)


async def init_superuser():
    """创建超级管理员（如果不存在）"""
    # 确保角色已存在
    superuser_role = await get_or_create_role("superuser", "超级管理员")

    try:
        # 获取现有超级管理员用户
        await User.get(username="admin")
        logger.info("超级管理员已存在")
    except DoesNotExist:
        # 生成安全的密码哈希
        # 创建新用户
        user = User(
            username="admin",
            role=superuser_role,
            is_active=False
        )
        user.password = "111111aA"
        await user.save()
        logger.info("超级管理员创建成功")


async def init_project():
    """
    添加默认项目 Scent, GeneralMarket, GridView
    """
    project_list = ["Scnet", "GeneralMarket", "GridView"]
    for project_name in project_list:
        try:
            # 尝试获取现有的项目
            project = await Project.get(name=project_name)
            logger.info(f"项目 '{project_name}' 已存在")
        except DoesNotExist:
            # 如果项目不存在，则创建新项目
            project = await Project.create(
                name=project_name
                # 可以根据需要添加其他字段
            )
            logger.info(f"项目 '{project_name}' 创建成功")


async def init_env():
    """
    临时在这默认添加环境
    """
    # 获取admin用户
    try:
        admin_user = await User.get(username="admin")
    except DoesNotExist:
        logger.error("Admin user not found")
        return

    # 导入环境信息
    from app.config.env_infos import env_info

    # 遍历所有项目
    for project_name, env_list in env_info.items():
        try:
            # 获取项目
            project = await Project.get(name=project_name)
        except DoesNotExist:
            logger.warn(f"Project {project_name} not found, skipping...")
            continue

        # 遍历该项目下的所有环境
        for env_data in env_list:
            try:
                # 检查环境是否已存在
                existing_env = await Env.get(name=env_data["name"])
                logger.info(f"Environment {env_data['name']} already exists")
                continue
            except DoesNotExist:
                # 创建新环境
                # 在创建环境时处理组件信息
                env = await Env.create(
                    name=env_data["name"],
                    domain=env_data["domain"],
                    ac_domain=env_data["ac_domain"],
                    need_version=env_data["need_version"],
                    desc=env_data["desc"],
                    components=";".join(env_data.get("compoment", [])),  # 将组件列表用分号连接
                    user=admin_user,
                    project=project
                )

                logger.info(f"Created environment {env_data['name']} for project {project_name}")


async def add_components_to_project():
    """
    根据项目添加组件信息到Component表中
    """
    for project_name, component_data in component_info.items():
        # 获取项目实例
        project = await Project.get(name=project_name)
        # 遍历组件信息并添加到数据库
        for component_name, component_path in component_data.items():
            # 检查组件是否已存在
            component_exists = await Component.filter(name=component_name, project=project).exists()
            if not component_exists:
                # 创建新组件
                await Component.create(
                    name=component_name,
                    path=component_path,
                    project=project
                )


def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,  # type: ignore  # 忽略类型检查
            allow_origins=settings.CORS_ORIGINS,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(AuthMiddleware)  # type: ignore  # 忽略类型检查
    ]
    return middleware


async def init_data():
    await init_db()
    await init_menus()
    await init_roles()
    await init_superuser()
    await init_project()
    await init_env()
    await add_components_to_project()


async def start_scheduler():
    """
        启动定时任务调度器
    """
    if not scheduler.running:
        scheduler.start()
        logger.info("定时任务调度器启动成功")


async def shutdown_scheduler():
    """
        关闭定时任务调度器
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("定时任务调度器已关闭")


# 在应用启动时注册定时任务
def register_scheduled_jobs():
    """
        注册定时任务
    """
    scheduler.add_job(
        fetch_scnet_component_versions,
        IntervalTrigger(minutes=20),
        id='test_task',
        name='测试定时任务',
        replace_existing=True
    )

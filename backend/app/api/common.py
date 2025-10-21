from app.models import Role
from app.models import User
from tortoise.exceptions import DoesNotExist
from jose import jwt
from app.settings import settings  # 导入JWT配置
from datetime import timedelta, timezone
from app.schemas.user import *


def create_access_token(user: User) -> str:
    """生成JWT访问令牌"""
    # 设置Token有效期（30分钟）
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.TOKEN_TIME)

    # 构建Payload
    payload = {
        "sub": str(user.id),  # JWT标准字段，表示令牌主体
        "exp": exp,  # 令牌过期时间
        "iat": datetime.now(timezone.utc)  # 签发时间也使用UTC
    }

    # 生成加密Token
    return jwt.encode(
        claims=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


async def get_user_by_name(username: str) -> User | None:
    """
    根据用户名查询用户
    """
    try:
        user = await User.get(username=username)
    except DoesNotExist:
        return None
    else:
        return user  # 替换为实际数据库查询


async def get_role_menus(role_name: str):
    """
    查询菜单的树形结构
    """
    try:
        role = await Role.get(name=role_name).prefetch_related('menus')
    except DoesNotExist:
        return []
    assigned_menus = await role.menus.all().values(
        "id", "label", "path", "icon", "parent_id"
    )

    if not assigned_menus:
        return []

    menu_map = {item["id"]: {"data": item, "children": []} for item in assigned_menus}
    root_items = []

    for item in assigned_menus:
        parent_id = item["parent_id"]
        if parent_id in menu_map:
            menu_map[parent_id]["children"].append(item)
        else:
            root_items.append(item)  # 父菜单不在权限中，当前为根

    def build_tree(item):
        return MenuTreeSchema(
            path=item["path"] or "",
            label=item["label"],
            icon=item["icon"],
            children=[build_tree(child) for child in menu_map[item["id"]]["children"]]
        )

    return [build_tree(item) for item in root_items]

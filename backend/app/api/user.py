"""
存放用户相关的视图
"""
from fastapi import APIRouter, Query, Request
from app.schemas.response import ResponseSchema
from app.api.common import *

router = APIRouter()


@router.get("/info", summary="查询用户")
async def get_users(
        page: int = Query(1, ge=1),  # 页码，最小为 1
        size: int = Query(10, le=100),  # 每页数量，最大 100
        username: str = Query(None)
):
    """
    分页获取用户列表，包含角色名、状态等信息
    """
    # 计算偏移量
    skip = (page - 1) * size

    try:
        # 基础查询条件
        query = User.filter(is_delete=False)

        if username:
            query = query.filter(username=username)

        # 查询总数
        total = await query.count()

        # 查询分页数据并预加载角色
        users = await query.offset(skip).limit(size).prefetch_related('role').order_by('-id')

        # 构造返回数据
        user_list = []
        for user in users:
            user_data = {
                "id": user.id,
                "name": user.username,
                "role": getattr(user.role, "name", "未知角色") if user.role else "无角色",
                "state": 1 if user.is_active else 0,
                "create_time": user.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_time": user.last_login_time.strftime(
                    "%Y-%m-%d %H:%M:%S") if user.last_login_time else user.last_login_time
            }
            user_list.append(user_data)

        # 构建分页数据
        paginated_data = PaginatedData(data=user_list, total=total)

        return ResponseSchema.success(data=paginated_data)

    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/add_user", summary="添加用户")
async def create_user(data: UserCreateSchema):
    try:
        # 校验角色是否存在
        role = await Role.get_or_none(name=data.role)
        if not role:
            return ResponseSchema.error(msg=f"{data.role} Not Find!")

        # 检查用户名是否已存在
        if await User.filter(username=data.name).exists():
            return ResponseSchema.error(msg=f"{data.name} Is Exist!")

        # 使用带密码加密的方法创建用户
        user = await User.create_with_password(
            username=data.name,
            password="111111aA",
            role=role,
            is_active=False
        )
        return ResponseSchema.success(data="")
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/get_menu", response_model=ResponseSchema[List[MenuTreeSchema]], summary="用户查看菜单")
async def get_menu_tree(request: Request):
    """
    功能:
        根据当前用户登录的角色查询菜单
    """
    # 从中间件获取当前用户登录的信息
    current_user = request.state.current_user
    if not current_user:
        return ResponseSchema[List[MenuTreeSchema]].error(msg="Not Find User!", code=401)
    role_name = current_user["role"]
    # 根据当前角色查询菜单树形结构
    menus_tree = await get_role_menus(role_name)
    if menus_tree is None:
        return ResponseSchema[List[MenuTreeSchema]].error(msg="Not Find Menu!")
    return ResponseSchema[List[MenuTreeSchema]].success(data=menus_tree)


@router.delete("/delete_user", summary="删除用户")
async def delete_user(data: UserIdSchema):
    try:
        # 检查用户是否存在
        user = await User.get_or_none(id=data.user_id)
        if not user:
            return ResponseSchema.error(msg="用户不存在！")

        # 检查是否为admin用户，如果是则不允许删除
        if user.username == "admin":
            return ResponseSchema.error(msg="不允许删除admin用户！", code=400)

        # 软删除用户（将is_delete设置为True,用户名设置为_d）
        user.username = user.username + "_d"
        user.is_delete = True
        await user.save()

        return ResponseSchema.success(data="", msg="用户删除成功")
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/reset_password", summary="重置用户密码")
async def reset_password(data: UserIdSchema):
    try:
        # 检查用户是否存在
        user = await User.get_or_none(id=data.user_id)
        if not user:
            return ResponseSchema.error(msg="用户不存在！")
        # 检查是否为admin用户，如果是则不允许删除
        if user.username == "admin":
            return ResponseSchema.error(msg="不允许重置admin用户的密码！", code=400)
        user.password = "111111aA"
        await user.save()

        return ResponseSchema.success(data="", msg="用户密码重置成功")
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)

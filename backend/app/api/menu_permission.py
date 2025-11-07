"""
菜单权限管理API
提供角色菜单权限的可视化配置接口
"""
from fastapi import APIRouter, Request, Path, Body
from app.schemas.response import ResponseSchema
from app.models import Role, Menu
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction
from typing import List
from pydantic import BaseModel, Field

router = APIRouter()


class RoleInfo(BaseModel):
    """角色信息响应模型"""
    id: int
    name: str
    desc: str
    is_readonly: bool


class MenuNode(BaseModel):
    """菜单树节点模型"""
    id: int
    label: str
    path: str | None
    icon: str | None
    parent_id: int | None
    children: List['MenuNode'] = []


class RoleMenusInfo(BaseModel):
    """角色菜单权限信息"""
    role_id: int
    role_name: str
    menu_ids: List[int]


class UpdateRoleMenusRequest(BaseModel):
    """更新角色菜单权限请求模型"""
    menu_ids: List[int] = Field(..., min_length=1, description="菜单ID列表，不能为空")


# 允许前向引用
MenuNode.model_rebuild()


def check_superuser(request: Request):
    """检查当前用户是否为超级管理员"""
    current_user = request.state.current_user
    if not current_user:
        return False, "未登录"
    
    if current_user.get("role") != "superuser":
        return False, "无权限访问，仅超级管理员可访问"
    
    return True, ""


@router.get("/roles", summary="获取角色列表", response_model=ResponseSchema[List[RoleInfo]])
async def get_roles(request: Request):
    """
    获取所有角色列表
    
    权限：仅超级管理员可访问
    
    返回：
    - 角色ID、名称、描述
    - is_readonly标识超级管理员角色为只读
    """
    # 权限验证
    is_allowed, msg = check_superuser(request)
    if not is_allowed:
        return ResponseSchema.error(msg=msg, code=403)
    
    try:
        # 查询所有角色
        roles = await Role.all().order_by('id')
        
        role_list = []
        for role in roles:
            role_list.append(RoleInfo(
                id=role.id,
                name=role.name,
                desc=role.desc,
                is_readonly=(role.name == "superuser")  # 超级管理员为只读
            ))
        
        return ResponseSchema.success(data=role_list)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/menus", summary="获取所有菜单树", response_model=ResponseSchema[List[MenuNode]])
async def get_menus(request: Request):
    """
    获取完整的菜单树结构
    
    权限：仅超级管理员可访问
    
    返回：
    - 树形结构的菜单列表
    - 包含菜单ID、名称、路径、图标等信息
    """
    # 权限验证
    is_allowed, msg = check_superuser(request)
    if not is_allowed:
        return ResponseSchema.error(msg=msg, code=403)
    
    try:
        # 查询所有菜单
        all_menus = await Menu.all().order_by('id')
        
        # 构建菜单字典
        menu_dict = {}
        for menu in all_menus:
            menu_dict[menu.id] = {
                "id": menu.id,
                "label": menu.label,
                "path": menu.path,
                "icon": menu.icon,
                "parent_id": menu.parent_id,
                "children": []
            }
        
        # 构建树形结构
        root_menus = []
        for menu in all_menus:
            if menu.parent_id is None:
                # 根菜单
                root_menus.append(menu_dict[menu.id])
            else:
                # 子菜单，添加到父菜单的children中
                if menu.parent_id in menu_dict:
                    menu_dict[menu.parent_id]["children"].append(menu_dict[menu.id])
        
        return ResponseSchema.success(data=root_menus)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/roles/{role_id}/menus", summary="获取角色菜单权限", 
            response_model=ResponseSchema[RoleMenusInfo])
async def get_role_menus(request: Request, role_id: int = Path(..., description="角色ID")):
    """
    获取指定角色的菜单权限
    
    权限：仅超级管理员可访问
    
    参数：
    - role_id: 角色ID
    
    返回：
    - 角色ID、名称
    - 该角色拥有的菜单ID列表
    """
    # 权限验证
    is_allowed, msg = check_superuser(request)
    if not is_allowed:
        return ResponseSchema.error(msg=msg, code=403)
    
    try:
        # 查询角色
        role = await Role.get_or_none(id=role_id).prefetch_related('menus')
        if not role:
            return ResponseSchema.error(msg="角色不存在", code=404)
        
        # 获取角色关联的菜单ID列表
        menus = await role.menus.all()
        menu_ids = [menu.id for menu in menus]
        
        result = RoleMenusInfo(
            role_id=role.id,
            role_name=role.name,
            menu_ids=menu_ids
        )
        
        return ResponseSchema.success(data=result)
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.put("/roles/{role_id}/menus", summary="更新角色菜单权限",
            response_model=ResponseSchema[RoleMenusInfo])
async def update_role_menus(
    request: Request,
    role_id: int = Path(..., description="角色ID"),
    data: UpdateRoleMenusRequest = Body(...)
):
    """
    更新指定角色的菜单权限
    
    权限：仅超级管理员可访问
    
    参数：
    - role_id: 角色ID
    - menu_ids: 菜单ID列表（不能为空）
    
    业务规则：
    - 不允许修改超级管理员角色的权限
    - 提交的菜单ID必须全部有效
    - 使用事务确保数据一致性
    
    返回：
    - 更新后的角色菜单权限信息
    """
    # 权限验证
    is_allowed, msg = check_superuser(request)
    if not is_allowed:
        return ResponseSchema.error(msg=msg, code=403)
    
    try:
        # 查询角色
        role = await Role.get_or_none(id=role_id)
        if not role:
            return ResponseSchema.error(msg="角色不存在", code=404)
        
        # 不允许修改超级管理员角色的权限
        if role.name == "superuser":
            return ResponseSchema.error(
                msg="不允许修改超级管理员角色的权限，该角色始终拥有所有菜单权限",
                code=400
            )
        
        # 验证所有菜单ID是否有效
        menu_ids = data.menu_ids
        menus = await Menu.filter(id__in=menu_ids).all()
        
        if len(menus) != len(menu_ids):
            valid_ids = {menu.id for menu in menus}
            invalid_ids = [mid for mid in menu_ids if mid not in valid_ids]
            return ResponseSchema.error(
                msg=f"以下菜单ID无效: {invalid_ids}",
                code=400
            )
        
        # 使用事务更新权限
        async with in_transaction():
            # 预加载关联关系
            role = await Role.get(id=role_id).prefetch_related('menus')
            
            # 清空旧的菜单关联
            await role.menus.clear()
            
            # 添加新的菜单关联
            await role.menus.add(*menus)
        
        # 返回更新后的信息
        result = RoleMenusInfo(
            role_id=role.id,
            role_name=role.name,
            menu_ids=menu_ids
        )
        
        return ResponseSchema.success(data=result, msg="菜单权限更新成功")
        
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)

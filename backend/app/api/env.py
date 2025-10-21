from fastapi import APIRouter, Request
from app.models.env import Project, Env, ComponentVersion
from app.schemas.response import ResponseSchema
from app.schemas.env import EnvCreateSchema, ProjectCreateSchema, RefreshEnvVersionsRequest

router = APIRouter()


@router.post("/add_project", summary="添加项目")
async def add_project(project_data: ProjectCreateSchema):
    try:
        # 检查项目名是否已存在
        existing_project = await Project.filter(name=project_data.name).first()
        if existing_project:
            return ResponseSchema.error(msg=f"项目名称 '{project_data.name}' 已存在")

        # 创建新项目
        project = await Project.create(
            name=project_data.name,
            desc=project_data.desc
        )

        return ResponseSchema.success(data={"id": project.id}, msg="项目创建成功")
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/projects", summary="查询所有项目")
async def list_projects():
    """
    查询所有的项目
    """
    try:
        # 获取所有项目
        projects = await Project.all()

        # 转换为字典列表
        project_list = [
            {
                "id": project.id,
                "name": project.name,
                "desc": project.desc
            }
            for project in projects
        ]

        return ResponseSchema.success(data=project_list)
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/project_envs", summary="获取所有项目及其环境信息")
async def list_projects_with_envs():
    """
    获取所有的项目和项目下的环境信息
    """
    try:
        # 获取所有项目
        projects = await Project.all().prefetch_related("envs")

        # 构建项目和环境的数据结构
        result = []
        for project in projects:
            # 获取该项目下的所有环境
            envs = await project.envs.all()

            # 构建环境列表
            env_list = [
                {
                    "id": env.id,
                    "name": env.name,
                    "domain": env.domain,
                    "need_version": env.need_version,
                    "desc": env.desc
                }
                for env in envs if env.need_version
            ]

            # 添加项目信息和其环境列表
            result.append({
                "id": project.id,
                "name": project.name,
                "desc": project.desc,
                "envs": env_list
            })

        return ResponseSchema.success(data=result)
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/env_versions", summary="分页查询环境版本信息(flag=1)")
async def list_env_versions_flagged(
        project_name: str,
        env_name: str,
        page: int = 1,
        size: int = 10
):
    """
    根据项目名称和环境名称分页查询环境的版本信息，只返回flag为1的版本

    Args:
        project_name (str): 项目名称
        env_name (str): 环境名称
        page (int): 页码，默认为1
        size (int): 每页数量，默认为10
    """
    try:
        # 检查项目是否存在
        project = await Project.get_or_none(name=project_name)
        if not project:
            return ResponseSchema.error(msg=f"项目名称 '{project_name}' 不存在")

        # 检查环境是否存在
        env = await Env.get_or_none(name=env_name, project=project)
        if not env:
            return ResponseSchema.error(msg=f"环境名称 '{env_name}' 在项目 '{project_name}' 中不存在")

        # 分页查询flag为1的版本信息，按创建时间倒序排列
        version_query = ComponentVersion.filter(env=env, flag=1)
        total = await version_query.count()
        versions = await version_query.offset((page - 1) * size).limit(size).prefetch_related("component")

        # 软去重：对于相同组件，只保留第一个（最新的）版本记录
        seen_components = set()
        version_list = []

        for version in versions:
            component_id = version.component.id if version.component else None

            # 如果是该组件的第一个版本记录，则添加到结果列表
            if component_id not in seen_components:
                seen_components.add(component_id)
                version_list.append({
                    "id": version.id,
                    "version": version.version,
                    "component": {
                        "id": version.component.id,
                        "name": version.component.name
                    } if version.component_id else None,
                    "created_at": version.created_time.strftime("%Y-%m-%d %H:%M:%S") if version.created_time else None,
                    "updated_at": version.updated_time.strftime("%Y-%m-%d %H:%M:%S") if version.updated_time else None,
                    "compare": ""
                })

        return ResponseSchema.success(data={
            "total": total,
            "page": page,
            "size": size,
            "versions": version_list
        })
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/add_env", summary="添加环境")
async def add_env(env_data: EnvCreateSchema, request: Request):
    try:
        # 检查环境名是否已存在
        existing_env = await Env.filter(name=env_data.name).first()
        if existing_env:
            return ResponseSchema.error(msg=f"环境名称 '{env_data.name}' 已存在")

        # 从中间件获取当前用户登录的信息
        current_user = request.state.current_user
        if not current_user:
            return ResponseSchema.error(msg="Not Find User!", code=401)
        user_id = current_user["id"]

        # 检查项目是否存在
        project = await Project.get_or_none(id=env_data.project_id)
        if not project:
            return ResponseSchema.error(msg=f"项目ID '{env_data.project_id}' 不存在")

        # 创建新环境
        env = await Env.create(
            name=env_data.name,
            domain=env_data.domain,
            need_version=env_data.need_version,
            desc=env_data.desc,
            user_id=user_id,
            project_id=env_data.project_id
        )

        return ResponseSchema.success(data={"id": env.id}, msg="环境创建成功")
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.get("/envs", summary="分页获取环境信息")
async def list_envs(
        project_name: str,
        page: int = 1,
        size: int = 10
):
    try:
        # 检查项目是否存在
        project = await Project.get_or_none(name=project_name)
        if not project:
            return ResponseSchema.error(msg=f"项目名称 '{project_name}' 不存在")

        # 分页查询环境信息
        env_query = Env.filter(project_id=project.id)
        total = await env_query.count()
        envs = await env_query.offset((page - 1) * size).limit(size).prefetch_related("user", "project")

        # 转换为字典列表
        env_list = []
        for env in envs:
            env_list.append({
                "id": env.id,
                "name": env.name,
                "domain": env.domain,
                "ac_domain": env.ac_domain,
                "need_version": env.need_version,
                "desc": env.desc,
                "updated_at": env.updated_time.strftime("%Y-%m-%d %H:%M:%S") if env.updated_time else None,
                "user": {
                    "id": env.user.id,
                    "username": env.user.username
                } if env.user else None,
                "project": {
                    "id": env.project.id,
                    "name": env.project.name
                } if env.project else None
            })

        return ResponseSchema.success(data={
            "total": total,
            "page": page,
            "size": size,
            "envs": env_list
        })
    except Exception as e:
        return ResponseSchema.error(msg=f"服务器错误: {str(e)}", code=500)


@router.post("/refresh_env_versions", summary="强制刷新环境版本信息")
async def refresh_env_versions(request_data: RefreshEnvVersionsRequest):
    """
    强制刷新指定环境的组件版本信息

    Args:
        project_name (str): 项目名称
        env_name (str): 环境名称
    """
    try:
        project_name = request_data.project_name
        env_name = request_data.env_name
        # 检查项目是否存在
        project = await Project.get_or_none(name=project_name)
        if not project:
            return ResponseSchema.error(msg=f"项目名称 '{project_name}' 不存在")

        # 检查环境是否存在
        env = await Env.get_or_none(name=env_name, project=project)
        if not env:
            return ResponseSchema.error(msg=f"环境名称 '{env_name}' 在项目 '{project_name}' 中不存在")

        # 调用后台任务强制刷新版本信息
        from app.core.background_task import fetch_scnet_component_versions

        await fetch_scnet_component_versions(name=env_name)

        return ResponseSchema.success(msg="success")
    except Exception as e:
        return ResponseSchema.error(msg=f"刷新失败: {str(e)}", code=500)

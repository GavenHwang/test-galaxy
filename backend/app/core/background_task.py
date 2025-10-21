import aiohttp
from app.models.env import Env, Component, ComponentVersion
from urllib.parse import urljoin
import asyncio
from app.log import logger
from tortoise.exceptions import DoesNotExist


async def fetch_scnet_component_versions(name=None):
    """
        获取scnet项目的版本
    """
    try:
        if name:
            environments = await Env.filter(need_version=True, project__name="Scnet", name=name).prefetch_related(
                "project")
        else:
            environments = await Env.filter(need_version=True, project__name="Scnet").prefetch_related("project")
        # 创建 aiohttp session
        async with aiohttp.ClientSession() as session:
            tasks = []
            for env in environments:
                # 为每个环境创建任务
                task = process_environment_versions(session, env)
                tasks.append(task)

            # 并发执行所有任务
            await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"执行定时任务 -> 获取Scnet项目的环境版本信息失败: {e}")


async def process_environment_versions(session, env):
    """
        处理单个环境的版本信息获取
        Args:
            session: aiohttp session
            env: 环境对象
    """
    try:
        # 获取环境对应的组件信息
        env_components = env.components.split(";")
        if not env_components:
            logger.error(f"环境 {env.name} 没有关联的组件信息")
            return
        for component_name in env_components:
            logger.info(f"获取环境：{env.name} 组件 {component_name} 的版本信息")
            # 查找数据库中的组件
            # 修改为使用 get_or_none 并添加适当的异常处理
            try:
                component = await Component.get_or_none(name=component_name.strip(), project=env.project)
                if not component:
                    logger.error(f"环境 {env.name} 的组件 {component_name} 在项目 {env.project.name} 中未找到")
                    continue
            except Exception as e:
                logger.error(f"查询环境 {env.name} 的组件 {component_name} 时发生错误: {e}")
                continue

            # 拼接url
            if component_name in ["sacp-ui", "learning-ui"] and env.ac_domain:
                full_url = urljoin(env.ac_domain.rstrip('/') + '/', component.path.lstrip('/'))
            else:
                full_url = urljoin(env.domain.rstrip('/') + '/', component.path.lstrip('/'))
            # 获取版本号
            version = await fetch_version_from_url(session, full_url)
            # 查询组件版本表中是否存在当前环境当前组件的当前版本信息
            logger.info(f"环境：{env.name} 组件：{component_name} 版本：{version}")
            try:
                mysql_version = await ComponentVersion.get(component_id=component.id, env=env, flag=1)
                if mysql_version.version == version:
                    # 获取版本时间
                    await mysql_version.save()
                else:
                    # 修改标志位
                    mysql_version.flag = 0
                    await mysql_version.save()
                    # 创建一个新的版本记录
                    await ComponentVersion.create(
                        component_id=component.id,
                        env=env,
                        version=version,
                        flag=1
                    )
            except DoesNotExist:
                # 创建版本记录
                await ComponentVersion.create(
                    component_id=component.id,
                    env=env,
                    version=version,
                    flag=1
                )
    except Exception as e:
        logger.error(f"获取Scnet项目的环境{env.name}版本信息失败: {e}")
        return


async def fetch_version_from_url(session, url):
    """
    从指定URL获取版本信息

    Args:
        session: aiohttp session
        url: 请求的URL

    Returns:
        str: 版本号，如果获取失败则返回None
    """
    try:
        logger.info(f"请求 {url}")
        async with session.get(url, ssl=False, timeout=aiohttp.ClientTimeout(total=1)) as response:
            if response.status == 200:
                content = await response.text()
                # 这里可以根据实际返回内容提取版本号
                # 示例：假设版本号在HTML中的某个位置
                version = content.strip("/n")
                if len(version) > 300:
                    return "error"
                return version
            else:
                logger.error(f"请求 {url} 失败，状态码: {response.status}")
                return "error"
    except asyncio.TimeoutError:
        logger.error(f"请求 {url} 超时")
        return "error"
    except Exception as e:
        logger.error(f"请求 {url} 时出错: {e}")
        return "error"

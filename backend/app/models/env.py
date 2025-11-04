from tortoise import fields
from app.models.base import BaseModel, TimestampMixin

__all__ = ['Env', 'Component', 'ComponentVersion', 'Project']


class Env(BaseModel, TimestampMixin):
    """环境表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description='环境名称')
    domain = fields.CharField(max_length=255, description='环境域名')
    ac_domain = fields.CharField(max_length=255, description='AC环境域名')
    need_version = fields.BooleanField(default=False, description='是否需要获取版本号')
    desc = fields.CharField(max_length=255, null=True, description='环境描述')
    components = fields.TextField(description='组件信息，多个组件用分号分隔')
    user = fields.ForeignKeyField('models.User', related_name='envs', description='关联用户（外键）')
    project = fields.ForeignKeyField('models.Project', related_name='envs', description='关联项目（外键）')

    class Meta(BaseModel.Meta):
        table = 'env'
        abstract = False


class Component(BaseModel, TimestampMixin):
    """组件表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description='组件名称')
    path = fields.CharField(max_length=255, description='组件路径')
    project = fields.ForeignKeyField('models.Project', related_name='components', description='关联项目（外键）')

    class Meta(BaseModel.Meta):
        table = 'component'
        abstract = False


class ComponentVersion(BaseModel, TimestampMixin):
    """组件版本表"""
    id = fields.IntField(pk=True)
    version = fields.CharField(max_length=50, description='版本号')
    flag = fields.IntField(default=0, description='版本标志，0表示历史版本，1表示当前版本')
    component = fields.ForeignKeyField('models.Component', related_name='versions', description='关联组件（外键）')
    env = fields.ForeignKeyField('models.Env', related_name='versions', description='关联环境（外键）')

    class Meta(BaseModel.Meta):
        table = 'component_version'
        abstract = False


class Project(BaseModel, TimestampMixin):
    """项目表"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description='项目名称')
    desc = fields.CharField(max_length=255, null=True, description='项目描述')

    class Meta(BaseModel.Meta):
        table = 'project'
        abstract = False

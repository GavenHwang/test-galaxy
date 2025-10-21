import bcrypt
from tortoise import fields
from tortoise.indexes import Index

from .base import BaseModel, TimestampMixin


class User(BaseModel, TimestampMixin):
    """
    用户模型
    包含基本用户信息和认证相关字段
    """
    id = fields.IntField(pk=True, description='用户唯一标识')
    username = fields.CharField(max_length=50, unique=True, index=True, description='用户名')
    _password = fields.CharField(max_length=255, description='密码哈希值',
                                custom_validator=lambda x: len(x) >= 60)  # 假设使用bcrypt哈希
    is_active = fields.BooleanField(default=True, index=True, description='账号激活状态')
    is_delete = fields.BooleanField(default=False, description='账号是否删除')
    last_login_time = fields.DatetimeField(null=True, index=True, description='最后登录时间')
    role = fields.ForeignKeyField('models.Role', related_name='users', n_delete=fields.CASCADE, description='关联角色')

    class Meta:
        table = 'user'
        indexes = (
            # 复合索引（标准写法）
            Index(
                fields=("is_active", "last_login_time"),
                name="idx_active_user_login_composite"
            ),
            # 单列索引
            Index(
                fields=("username",),
                name="idx_username_unique"
            )
        )

    @property
    def password(self) -> str:
        """密码脱敏显示"""
        return "**********"

    @password.setter
    def password(self, raw_password: str):
        """自动哈希密码"""
        if not raw_password:
            raise ValueError("密码不能为空")
        # 生成盐值并哈希
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(raw_password.encode(), salt)
        self._password = hashed.decode()  # 转为字符串存储

    @classmethod
    async def create_with_password(cls, username: str, password: str, **kwargs):
        """
        创建带密码的用户
        
        Args:
            username: 用户名
            password: 明文密码
            **kwargs: 其他用户字段
            
        Returns:
            User: 创建的用户实例
            
        Raises:
            ValueError: 当密码不符合要求时
        """
        # 验证密码是否符合安全规范
        if not password:
            raise ValueError("密码不能为空")
        if len(password) < 8 or len(password) > 50:
            raise ValueError("密码长度必须在8-50个字符之间")
        if not any(c.islower() for c in password) or not any(c.isupper() for c in password) or not any(c.isdigit() for c in password):
            raise ValueError("密码必须包含大小写字母和数字")
            
        # 创建用户实例
        user = cls(username=username, **kwargs)
        user.password = password  # 使用现有的password setter进行哈希处理
        await user.save()
        return user

    async def authenticate(self, password: str) -> bool:
        """验证明文密码与存储的哈希值是否匹配"""
        return bcrypt.checkpw(password.encode(), self._password.encode())

    def __str__(self):
        return self.username


class Role(BaseModel, TimestampMixin):
    """
    角色模型
    用于定义用户权限集合
    """
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=50, unique=True, description='角色名称')
    desc = fields.CharField(max_length=50, unique=True, description='角色描述')
    menus = fields.ManyToManyField("models.Menu", related_name="role_menus")

    class Meta:
        table = 'role'

    def __str__(self):
        return self.name


class Menu(BaseModel, TimestampMixin):
    """
    菜单模型（支持树形结构 + 角色权限控制）
    """
    # 基础信息
    id = fields.IntField(pk=True, description="菜单唯一标识")
    label = fields.CharField(max_length=50, index=True, description="菜单名称（带索引，快速查询）")
    path = fields.CharField(max_length=255, null=True, description="菜单路由地址（可为空，如按钮无路由）")
    icon = fields.CharField(max_length=100, null=True, description="菜单图标（支持l图标库类名或SVG路径）")
    parent = fields.ForeignKeyField(
        "models.Menu",
        related_name="children",
        on_delete=fields.SET_NULL,
        null=True,
        description="父菜单（关联自身，支持递归查询）"
    )

    class Meta:
        table = "menu"

    async def get_all_children(self):
        children = await self.children.all()
        all_children = []
        for child in children:
            all_children.append(child)
            all_children.extend(await child.get_all_children())
        return all_children
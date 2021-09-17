from django.db import models
from common.model import BaseModel
from tenant.models import Tenant
from inventory.models import User, Permission


class ChildManager(BaseModel):
    # 子管理员
    # manager_visible 所在分组 所在分组的下级分组 指定分组与账号
    # manager_permission 全部权限 指定权限 所有应用权限
    # {
    #     "manager_visible": ["所在分组","指定分组与账号"],
    #     "manager_permission": "指定权限",
    #     "assign_group": [],
    #     "assign_user": [],
    #     "assign_permission": [""]
    # }

    class Meta:
        app_label = 'childmanager'

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return self.user.username

    @property
    def name(self):
        return self.user.nickname

    @property
    def manager_visible(self):
        data = self.data
        return data.get('manager_visible')

    @property
    def assign_group(self):
        data = self.data
        return data.get('assign_group')

    @property
    def assign_user(self):
        data = self.data
        return data.get('assign_user')

    @property
    def manager_permission(self):
        data = self.data
        return data.get('manager_permission')
    
    @property
    def assign_permission_uuid(self):
        data = self.data
        assign_permission = data.get('assign_permission', [])
        return assign_permission

    @property
    def assign_permission(self):
        data = self.data
        assign_permission = data.get('assign_permission', [])
        items = []
        if assign_permission:
            permissions = Permission.valid_objects.filter(uuid__in=assign_permission)
            for permission in permissions:
                items.append(permission.name)
        return items
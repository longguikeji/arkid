import os
import django

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()

from arkid.core.models import Tenant, Permission, User
from arkid.core.perm.permission_data import PermissionData
permission_id = ''
permission = Permission.valid_objects.filter(id=permission_id).first()
tenant = Tenant.valid_objects.filter(slug='admin').first()
users = User.valid_objects.filter(tenant_id=tenant.id)
print('用户数：'+str(len(users)))
ids = []
ids.append(str(permission.id))
if permission.category == 'group' and permission.container.all():
    for item in permission.container.all():
        if str(item.id) not in ids:
            ids.append(str(item.id))
data = {
    'ids': ids,
    'app_id': permission.app_id,
    'tenant_id': str(tenant.id)
}
print(data)
pd = PermissionData()
pd.update_open_other_user_app_permission(data)
import os
import django

# 导入settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "arkid.settings")
# 安装django
django.setup()

from arkid.core.models import User, Tenant, UserPermissionResult

# tenants = Tenant.valid_objects.all()
users = User.valid_objects.all()
# print('total:'+str(len(tenants)))

# for tenant in tenants:
#     print('-----------------begin--------------')
#     print('tenant name:'+tenant.name)
#     for user in users:
#         is_admin = tenant.has_admin_perm(user)
#         if is_admin and UserPermissionResult.valid_objects.filter(tenant=tenant, app=None, user=user).exists():
#             # 重复添加不会有问题，只会保留一个
#             print('add admin in tenant users:'+user.username)
#             tenant.users.add(user)
#             tenant.save()
#     print('-----------------end--------------')

# 如果有用户没在tenant.users里手动加进去
print('total:'+str(len(users)))
for index, user in enumerate(users):
    print('index:'+str(index))
    tenant = user.tenant
    tenant.users.add(user)
    tenant.save()
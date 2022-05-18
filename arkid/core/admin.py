from django.contrib import admin
from .models import(
    User, UserGroup, Tenant,
    App, AppGroup, Permission,
    Approve, ExpiringToken, TenantConfig,
    UserPermissionResult, SystemPermission,
)

admin.site.register(Tenant)
admin.site.register(User)
admin.site.register(UserGroup)
admin.site.register(App)
admin.site.register(AppGroup)
admin.site.register(Permission)
admin.site.register(Approve)
admin.site.register(ExpiringToken)
admin.site.register(SystemPermission)
admin.site.register(UserPermissionResult)
admin.site.register(TenantConfig)

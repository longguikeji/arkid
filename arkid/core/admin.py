from django.contrib import admin
from .models import(
    User, UserGroup, Tenant,
    App, AppGroup, Permission,
    Approve, ExpiringToken, TenantConfig,
    ApiPermission,
)

admin.site.register(Tenant)
admin.site.register(User)
admin.site.register(UserGroup)
admin.site.register(App)
admin.site.register(AppGroup)
admin.site.register(Permission)
admin.site.register(Approve)
admin.site.register(ExpiringToken)
admin.site.register(ApiPermission)
admin.site.register(TenantConfig)


from django.contrib import admin
from .models import(
    Tenant, TenantConfig, TenantPasswordComplexity,
    TenantContactsConfig, TenantContactsUserFieldConfig, TenantContactsGroupConfig,
    TenantDesktopConfig,
)

admin.site.register(Tenant)
admin.site.register(TenantConfig)
admin.site.register(TenantPasswordComplexity)
admin.site.register(TenantContactsConfig)
admin.site.register(TenantContactsUserFieldConfig)
admin.site.register(TenantContactsGroupConfig)
admin.site.register(TenantDesktopConfig)

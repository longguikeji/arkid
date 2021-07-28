from django.contrib import admin
from .models import Tenant, TenantConfig, TenantPasswordComplexity, TenantContactsConfig

admin.site.register(Tenant)
admin.site.register(TenantConfig)
admin.site.register(TenantPasswordComplexity)
admin.site.register(TenantContactsConfig)

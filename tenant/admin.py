from django.contrib import admin
from .models import Tenant, TenantConfig, TenantPasswordComplexity

admin.site.register(Tenant)
admin.site.register(TenantConfig)
admin.site.register(TenantPasswordComplexity)

from django.contrib import admin
from .models import Tenant, TenantConfig

admin.site.register(Tenant)
admin.site.register(TenantConfig)

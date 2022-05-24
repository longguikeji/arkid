from django.contrib import admin
from .models import Extension, TenantExtensionConfig

admin.site.register(Extension)
admin.site.register(TenantExtensionConfig)
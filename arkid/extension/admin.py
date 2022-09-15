from django.contrib import admin
from .models import Extension, TenantExtension, TenantExtensionConfig, ArkStoreCategory

admin.site.register(Extension)
admin.site.register(TenantExtension)
admin.site.register(TenantExtensionConfig)
admin.site.register(ArkStoreCategory)
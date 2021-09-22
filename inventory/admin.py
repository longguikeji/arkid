from django.contrib import admin
from .models import(
    User, Group, Permission,
    UserPassword, UserAppData, CustomField,
    PermissionGroup,
)

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(UserPassword)
admin.site.register(UserAppData)
admin.site.register(CustomField)
admin.site.register(PermissionGroup)

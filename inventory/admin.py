from django.contrib import admin
from .models import(
    User, Group, Permission,
    UserPassword, UserAppData,
)
admin.site.register(User)
admin.site.register(Group)
admin.site.register(Permission)
admin.site.register(UserPassword)
admin.site.register(UserAppData)

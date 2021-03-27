from django.contrib import admin
from .models import User, Group, Permission

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Permission)


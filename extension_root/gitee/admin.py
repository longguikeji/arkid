from django.contrib import admin
from extension_root.gitee.models import GiteeUser, GiteeInfo

admin.site.register(GiteeUser)
admin.site.register(GiteeInfo)

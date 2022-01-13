from django.contrib import admin
from extension_root.wechatwork.models import WeChatWorkUser, WeChatWorkInfo

admin.site.register(WeChatWorkUser)
admin.site.register(WeChatWorkInfo)

from django.contrib import admin
from extension_root.wechatscan.models import WeChatScanUser, WeChatScanInfo

admin.site.register(WeChatScanUser)
admin.site.register(WeChatScanInfo)

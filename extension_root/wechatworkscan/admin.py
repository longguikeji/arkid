from django.contrib import admin
from extension_root.wechatworkscan.models import WeChatWorkScanUser, WeChatWorkScanInfo

admin.site.register(WeChatWorkScanUser)
admin.site.register(WeChatWorkScanInfo)

from django.contrib import admin
from .models import WebHook, WebHookTriggerHistory


admin.site.register(WebHook)
admin.site.register(WebHookTriggerHistory)
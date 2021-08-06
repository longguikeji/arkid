from django.contrib import admin
from .models import Webhook, WebhookEvent, WebhookTriggerHistory


admin.site.register(Webhook)
admin.site.register(WebhookEvent)
admin.site.register(WebhookTriggerHistory)

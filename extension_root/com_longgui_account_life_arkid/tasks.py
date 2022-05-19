#!/usr/bin/env python3

from celery import shared_task
from arkid.common.logger import logger
from arkid.extension.models import TenantExtensionConfig, TenantExtension
from .models import UserExpiration
from django.utils import dateformat, timezone


@shared_task(bind=True)
def deactive_expired_user(self, config_id, *args, **kwargs):
    extension_config = TenantExtensionConfig.objects.get(id=config_id)
    tenant = extension_config.tenant
    user_expirations = UserExpiration.valid_objects.filter(user__tenant=tenant)
    for expiration in user_expirations:
        if expiration.expiration_time <= timezone.now():
            expiration.user.offline()

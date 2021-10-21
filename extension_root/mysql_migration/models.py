#!/usr/bin/env python3

import uuid
from django.db import models
from django.apps import AppConfig


class MysqlMigrationAppConfig(AppConfig):

    name = 'mysql_migration'


class V1UserIdUUID(models.Model):
    class meta:
        app_label = 'mysql_migration'

    v1_user_id = models.IntegerField()
    v1_user_uuid = models.UUIDField(
        verbose_name='UUID', default=uuid.uuid4, editable=True, unique=True
    )
    tenant_id = models.IntegerField()

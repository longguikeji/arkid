from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class ArkIDAppConfig(AppConfig):

    name = "arkid"


class ArkIDUser(BaseModel):
    class meta:

        app_label = "arkid"

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(
        User, verbose_name="用户", related_name="arkid_user", on_delete=models.PROTECT
    )
    arkid_user_id = models.CharField(
        max_length=255, blank=True, verbose_name="ArkID User ID"
    )

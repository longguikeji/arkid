from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from tenant.models import Tenant


class ArkIDAppConfig(AppConfig):

    name = "arkid_saas"


class LocalSaasArkIDBind(BaseModel):
    class meta:

        app_label = "arkid_saas"

    company_name = models.CharField(
        max_length=255, blank=False, verbose_name="本地ArkID公司名"
    )
    contact_person = models.CharField(max_length=128, blank=False)
    email = models.EmailField(blank=False)
    mobile = models.CharField(max_length=128, blank=False)

    local_tenant_uuid = models.UUIDField(verbose_name='本地ArkID UUID', unique=True, blank=False)
    local_tenant_slug = models.SlugField(verbose_name='本地ArkID短链接标识', blank=False)
    local_host = models.URLField(verbose_name='本地ArkID链接', blank=False)

    saas_tenant = models.OneToOneField(Tenant, on_delete=models.PROTECT, blank=False)

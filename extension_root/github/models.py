from django.db import models
from django.apps import AppConfig
from common.model import BaseModel
from inventory.models import User
from tenant.models import Tenant


class GithubAppConfig(AppConfig):

    name = 'github'


class GithubUser(BaseModel):

    class meta:

        app_label = 'github'

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    user = models.OneToOneField(User, verbose_name='用户', related_name='github_user', on_delete=models.PROTECT)
    github_user_id = models.CharField(max_length=255, blank=True, verbose_name='Github ID')
from django.db import models
from django.apps import AppConfig
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = 'com_longgui_external_idp_github'

class LongguiGithubAppConfig(AppConfig):

    name = app_label


class GithubUser(UserExpandAbstract):
    class Meta:
        app_label = app_label

    github_user_id = models.CharField(
        max_length=255, blank=True, verbose_name='Github ID'
    )
    github_nickname = models.CharField(
        max_length=255, blank=True, default='', verbose_name='昵称',
    )
    github_avatar = models.CharField(
        max_length=255, blank=True, default='', verbose_name='头像',
    )

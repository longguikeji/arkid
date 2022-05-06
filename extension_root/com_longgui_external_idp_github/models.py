from django.db import models
from django.apps import AppConfig
from arkid.core.expand import UserExpandAbstract
from arkid.core.translation import gettext_default as _


class LongguiGithubAppConfig(AppConfig):

    name = "com_longgui_external_idp_github"


class GithubUser(UserExpandAbstract):
    class Meta:

        app_label = "com_longgui_external_idp_github"

    github_user_id = models.CharField(
        max_length=255, blank=True, verbose_name='Github ID'
    )

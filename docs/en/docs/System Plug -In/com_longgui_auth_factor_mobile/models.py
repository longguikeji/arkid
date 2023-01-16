from django.db import models
from django.apps import AppConfig
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract

app_label = "com_longgui_auth_factor_mobile"


class LongguiMobileAppConfig(AppConfig):

    name = app_label


class UserMobile(UserExpandAbstract):
    class Meta:
        app_label = app_label

    mobile = models.CharField(_("Mobile", "电话号码"), max_length=256,blank=True,null=True)
    
    area_code = models.CharField(_("AreaCode","区号"), max_length=10, default="86")

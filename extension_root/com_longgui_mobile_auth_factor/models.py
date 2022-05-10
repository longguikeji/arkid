from django.db import models
from django.apps import AppConfig
from arkid.core.expand import UserExpandAbstract
from arkid.core.translation import gettext_default as _


class LongguiMobileAppConfig(AppConfig):

    name = "com_longgui_mobile_auth_factor"


class UserMobile(UserExpandAbstract):
    class Meta:

        app_label = "com_longgui_mobile_auth_factor"

    mobile = models.CharField(_("Mobile", "电话号码"), max_length=256)
    
    area_code = models.CharField(_("AreaCode","区号"), max_length=10, default="86")

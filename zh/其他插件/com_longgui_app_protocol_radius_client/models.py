
from arkid.core.translation import gettext_default as _
from django.apps import AppConfig
from arkid.core.models import UserExpandAbstract
app_label = 'com_longgui_app_protocol_radius_client'

class LongguiRadiusClientAppConfig(AppConfig):
    name = app_label
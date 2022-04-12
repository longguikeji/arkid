from django.db import models
from arkid.core.expand import UserExpandAbstract
from arkid.core.translation import gettext_default as _


class UserPassword(UserExpandAbstract):
    password = models.CharField(_("Password", "密码"), max_length=40, primary_key=True)

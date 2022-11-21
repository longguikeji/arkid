from django.db import models
from django.apps import AppConfig
from arkid.core.expand import create_expand_abstract_model
from arkid.core.translation import gettext_default as _
from arkid.core.models import UserExpandAbstract, User
from arkid.common.model import BaseModel

app_label = "com_longgui_auth_factor_webauthn"


class WebauthnAppConfig(AppConfig):

    name = app_label


class UserWebauthnCredential(BaseModel):
    class Meta:
        app_label = app_label

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User', '用户'),
        related_name="webauthn_credential_set",
        related_query_name="webauthn_credentials",
    )
    credential_id = models.CharField(_("Credential ID", "凭证ID"), max_length=256)
    credential = models.JSONField(
        blank=True, default=dict, verbose_name=_('Credential', '凭证')
    )

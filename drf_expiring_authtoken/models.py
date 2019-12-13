"""Expiring Token models.

Classes:
    ExpiringToken
"""
import os
import binascii

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from drf_expiring_authtoken.settings import token_settings
from oneid_meta.models import User

class ExpiringToken(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    user = models.OneToOneField(User, related_name='auth_token', on_delete=models.CASCADE, verbose_name=_("User"))
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ExpiringToken, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def expired(self):
        """Return boolean indicating token expiration."""
        now = timezone.now()
        if self.created < now - token_settings.EXPIRING_TOKEN_LIFESPAN:
            return True
        return False

    def __str__(self):
        return self.user.username

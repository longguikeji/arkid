# pylint: disable=missing-docstring

from django.contrib import admin

from ..drf_expiring_authtoken.models import ExpiringToken


class ExpiringTokenAdmin(admin.ModelAdmin):
    pass


admin.site.register(ExpiringToken, ExpiringTokenAdmin)

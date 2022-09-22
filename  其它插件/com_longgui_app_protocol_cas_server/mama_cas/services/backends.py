import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property


class ServiceConfig(object):
    PROXY_ALLOW_DEFAULT = False
    CALLBACKS_DEFAULT = []
    LOGOUT_ALLOW_DEFAULT = False
    LOGOUT_URL_DEFAULT = None

    @cached_property
    def services(self):
        services = []

        for service in getattr(settings, 'MAMA_CAS_SERVICES', []):
            service = service.copy()
            try:
                match = re.compile(service['SERVICE'])
            except KeyError:
                raise ImproperlyConfigured(
                    'Missing SERVICE key for service configuration. '
                    'Check your MAMA_CAS_VALID_SERVICES setting.')

            service['MATCH'] = match
            # TODO For transitional backwards compatibility, this defaults to True.
            service.setdefault('PROXY_ALLOW', True)
            service.setdefault('CALLBACKS', self.CALLBACKS_DEFAULT)
            service.setdefault('LOGOUT_ALLOW', self.LOGOUT_ALLOW_DEFAULT)
            service.setdefault('LOGOUT_URL', self.LOGOUT_URL_DEFAULT)
            try:
                service['PROXY_PATTERN'] = re.compile(service['PROXY_PATTERN'])
            except KeyError:
                pass
            services.append(service)

        return services

    def get_service(self, s):
        for service in self.services:
            if service['MATCH'].match(s):
                return service
        return {}

    def get_config(self, service, setting):
        """
        Access the configuration for a given service and setting. If the
        service is not found, return a default value.
        """
        try:
            return self.get_service(service)[setting]
        except KeyError:
            return getattr(self, setting + '_DEFAULT')

    def is_valid(self, s):
        if not self.services:
            return True
        return bool(self.get_service(s))


services = ServiceConfig()


class SettingsBackend(object):
    def get_callbacks(self, service):
        return services.get_config(service, 'CALLBACKS')

    def get_logout_url(self, service):
        return services.get_config(service, 'LOGOUT_URL')

    def logout_allowed(self, service):
        return services.get_config(service, 'LOGOUT_ALLOW')

    def proxy_allowed(self, service):
        return services.get_config(service, 'PROXY_ALLOW')

    def proxy_callback_allowed(self, service, pgturl):
        try:
            return services.get_config(service, 'PROXY_PATTERN').match(pgturl)
        except AttributeError:
            return False

    def service_allowed(self, service):
        if not service:
            return False
        return services.is_valid(service)

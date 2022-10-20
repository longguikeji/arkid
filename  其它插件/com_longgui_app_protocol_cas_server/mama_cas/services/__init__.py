import re
import warnings

from django.conf import settings
from django.utils.module_loading import import_string

MAMA_CAS_ATTRIBUTE_CALLBACKS = getattr(settings, 'MAMA_CAS_ATTRIBUTE_CALLBACKS', ('arkid_extensions.com_longgui_app_protocol_cas_server.mama_cas.callbacks.user_model_attributes',))

def _get_backends():
    """Retrieve the list of configured service backends."""
    backends = []
    backend_paths = getattr(
        settings, 'MAMA_CAS_SERVICE_BACKENDS',
        ['arkid_extensions.com_longgui_app_protocol_cas_server.mama_cas.services.backends.SettingsBackend']
    )
    for backend_path in backend_paths:
        backend = import_string(backend_path)()
        backends.append(backend)
    return backends


def _is_allowed(attr, *args):
    """
    Test if a given attribute is allowed according to the
    current set of configured service backends.
    """
    for backend in _get_backends():
        try:
            if getattr(backend, attr)(*args):
                return True
        except AttributeError:
            raise NotImplementedError("%s.%s.%s() not implemented" % (
                backend.__class__.__module__, backend.__class__.__name__, attr)
            )
    return False


def _is_valid_service_url(url):
    """Access services list from ``MAMA_CAS_VALID_SERVICES``."""
    valid_services = getattr(settings, 'MAMA_CAS_VALID_SERVICES', ())
    if not valid_services:
        return True
    warnings.warn(
        'The MAMA_CAS_VALID_SERVICES setting is deprecated. Services '
        'should be configured using MAMA_CAS_SERVICES.', DeprecationWarning)
    for service in [re.compile(s) for s in valid_services]:
        if service.match(url):
            return True
    return False


def get_backend_path(service):
    """Return the dotted path of the matching backend."""
    for backend in _get_backends():
        try:
            if backend.service_allowed(service):
                return "%s.%s" % (backend.__class__.__module__, backend.__class__.__name__)
        except AttributeError:
            raise NotImplementedError("%s.%s.service_allowed() not implemented" % (
                backend.__class__.__module__, backend.__class__.__name__)
            )
    return None


def get_callbacks(service):
    """Get configured callbacks list for a given service identifier."""
    callbacks = list(MAMA_CAS_ATTRIBUTE_CALLBACKS)
    if callbacks:
        warnings.warn(
            'The MAMA_CAS_ATTRIBUTE_CALLBACKS setting is deprecated. Service callbacks '
            'should be configured using MAMA_CAS_SERVICES.', DeprecationWarning)

    for backend in _get_backends():
        try:
            callbacks.extend(backend.get_callbacks(service))
        except AttributeError:
            raise NotImplementedError("%s.%s.get_callbacks() not implemented" % (
                backend.__class__.__module__, backend.__class__.__name__)
            )
    return callbacks


def get_logout_url(service):
    """Get the configured logout URL for a given service identifier, if any."""
    for backend in _get_backends():
        try:
            return backend.get_logout_url(service)
        except AttributeError:
            raise NotImplementedError("%s.%s.get_logout_url() not implemented" % (
                backend.__class__.__module__, backend.__class__.__name__)
            )
    return None


def logout_allowed(service):
    """Check if a given service identifier should be sent a logout request."""
    if hasattr(settings, 'MAMA_CAS_SERVICES'):
        return _is_allowed('logout_allowed', service)

    if hasattr(settings, 'MAMA_CAS_ENABLE_SINGLE_SIGN_OUT'):
        warnings.warn(
            'The MAMA_CAS_ENABLE_SINGLE_SIGN_OUT setting is deprecated. SLO '
            'should be configured using MAMA_CAS_SERVICES.', DeprecationWarning)
    return getattr(settings, 'MAMA_CAS_ENABLE_SINGLE_SIGN_OUT', False)


def proxy_allowed(service):
    """Check if a given service identifier is allowed to proxy requests."""
    return _is_allowed('proxy_allowed', service)


def proxy_callback_allowed(service, pgturl):
    """Check if a given proxy callback is allowed for the given service identifier."""
    if hasattr(settings, 'MAMA_CAS_SERVICES'):
        return _is_allowed('proxy_callback_allowed', service, pgturl)
    return _is_valid_service_url(service)


def service_allowed(service):
    """Check if a given service identifier is authorized."""
    if hasattr(settings, 'MAMA_CAS_SERVICES'):
        return _is_allowed('service_allowed', service)
    return _is_valid_service_url(service)

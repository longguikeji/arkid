try:
    from ipware import get_client_ip as _get_client_ip
except ModuleNotFoundError:
    _get_client_ip = lambda r: (None, None)
from .base import SETTINGS


def remove_secrets(data):
    data = data.copy()
    for key in SETTINGS['SECRETS']:
        if key in data:
            data[key] = '***'
    return data


def get_client_ip(request):
    return _get_client_ip(request)[0]

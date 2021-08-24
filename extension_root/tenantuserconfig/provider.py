import requests
from typing import Dict
from runtime import Runtime
from common.extension import InMemExtension
from common.provider import TenantUserConfigProvider
from .constants import KEY
from django.urls import reverse
from config import get_app_config


class TenantUserConfigIdpProvider(TenantUserConfigProvider):

    def __init__(self) -> None:
        super().__init__()

from typing import Dict
from app.models import App
from common.provider import AppTypeProvider
from oauth2_provider.models import Application
from django.urls import reverse
from config import get_app_config


class CasAppTypeProvider(AppTypeProvider):

    def create(self, app, data: Dict) -> Dict:
        host = get_app_config().get_host()
        uniformed_data = {
            'login': host+reverse("api:cas_server:cas_login", args=[app.tenant.uuid]),
            'validate': host+reverse("api:cas_server:cas_service_validate", args=[app.tenant.uuid]),
        }
        return uniformed_data

    def update(self, app, data: Dict) -> Dict:
        host = get_app_config().get_host()
        uniformed_data = {
            'login': host+reverse("api:cas_server:cas_login", args=[app.tenant.uuid]),
            'validate': host+reverse("api:cas_server:cas_service_validate", args=[app.tenant.uuid]),
        }
        return uniformed_data

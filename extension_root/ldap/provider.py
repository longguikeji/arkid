from typing import Dict
from app.models import App
from common.provider import AppTypeProvider


class LDAPAppTypeProvider(AppTypeProvider):

    def create(self, app, data: Dict):
        pass
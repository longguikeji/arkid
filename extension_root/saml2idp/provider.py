from django.urls.base import reverse
from app.models import App
from common.provider import AppTypeProvider
import os
from djangosaml2idp.scripts.idpinit import run as idp_init
from typing import Dict


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class SAML2IDPAppTypeProvider(AppTypeProvider):
    
    def __init__(self) -> None:
        idp_init()
        super().__init__()

    def create(self, app: App, data: Dict) -> Dict:
        data["idp_metadata"] = reverse("djangosaml2idp:metadata")
        return data

    def update(self, app: App, data: Dict) -> Dict:
        data["idp_metadata"] = reverse("djangosaml2idp:metadata")
        return data
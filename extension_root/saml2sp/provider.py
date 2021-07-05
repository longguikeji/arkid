from typing import Dict
from app.models import App
from common.provider import ExternalIdpProvider
from django.urls import reverse


class SAML2SPExternalIdpProvider(ExternalIdpProvider):

    def create(self, tenant_uuid, external_idp, data):
        return data

    def update(self, tenant_uuid, external_idp, data):
        return data
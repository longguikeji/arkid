from typing import Dict
from .user_info_manager import ArkIDUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, BIND_KEY
from django.urls import reverse
from config import get_app_config


class ArkIDExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = BIND_KEY
    name: str

    client_id: str
    secret_id: str
    login_url: str
    callback_url: str
    bind_url: str

    def __init__(self) -> None:
        super().__init__()

    def load_data(self, tenant_uuid):
        from tenant.models import Tenant
        from external_idp.models import ExternalIdp

        idp = ExternalIdp.active_objects.filter(
            tenant__uuid=tenant_uuid,
            type=KEY,
        ).first()
        assert idp is not None

        data = idp.data

        self.client_id = data.get('client_id')
        self.secret_id = data.get('secret_id')
        self.authorize_url = data.get('authorize_url')
        self.token_url = data.get('token_url')
        self.userinfo_url = data.get('userinfo_url')
        self.img_url = data.get('img_url')
        self.login_url = data.get('login_url')
        self.callback_url = data.get('callback_url')
        self.bind_url = data.get('bind_url')

    def create(self, tenant_uuid, external_idp, data):
        return {
            'client_id': data.get('client_id'),
            'secret_id': data.get('secret_id'),
            'authorize_url': data.get('authorize_url'),
            'token_url': data.get('token_url'),
            'userinfo_url': data.get('userinfo_url'),
            'img_url': data.get('img_url'),
            'login_url': reverse("api:arkid:login", args=[tenant_uuid]),
            'callback_url': reverse("api:arkid:callback", args=[tenant_uuid]),
            'bind_url': reverse("api:arkid:bind", args=[tenant_uuid]),
        }

    def bind(self, user: any, data: Dict):
        from .models import ArkIDUser

        ArkIDUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            arkid_user_id=data.get("user_id"),
        )

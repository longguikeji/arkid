from typing import Dict
from .user_info_manager import GithubUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, BIND_KEY, LOGIN_URL, IMG_URL
from django.urls import reverse
from config import get_app_config


class GithubExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = BIND_KEY
    name: str

    client_id: str
    secret_id: str

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

        client_id = data.get('client_id')
        secret_id = data.get('secret_id')
        login_url = data.get('login_url')
        callback_url = data.get('callback_url')
        bind_url = data.get('bind_url')

        self.client_id = client_id
        self.secret_id = secret_id
        self.login_url = login_url
        self.callback_url = callback_url
        self.bind_url = bind_url

    def create(self, tenant_uuid, external_idp, data):
        host = get_app_config().get_host()
        client_id = data.get('client_id')
        secret_id = data.get('secret_id')

        return {
            'client_id': client_id,
            'secret_id': secret_id,
            'login_url': host+reverse("api:github:login", args=[tenant_uuid]),
            'callback_url': host+reverse("api:github:callback", args=[tenant_uuid]),
            'bind_url': host+reverse("api:github:bind", args=[tenant_uuid]),
            'img_url': IMG_URL,
        }

    def bind(self, user: any, data: Dict):
        from .models import GithubUser

        GithubUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            github_user_id=data.get('user_id'),
        )

from typing import Dict
from .user_info_manager import GiteeUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, BIND_KEY, LOGIN_URL, IMG_URL
from django.urls import reverse


class GiteeExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = BIND_KEY
    name: str

    client_id: str
    secret_id: str
    login_url: str
    callback_url: str
    bind_url: str

    def __init__(self) -> None:
        super().__init__()

    def load_data(self, tenant_id):
        from tenant.models import Tenant
        from external_idp.models import ExternalIdp

        idp = ExternalIdp.objects.filter(
            tenant__id=tenant_id,
            type=KEY,
        )

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

    def create(self, tenant_id, external_idp, data):
        client_id = data.get('client_id')
        secret_id = data.get('secret_id')
        login_url = reverse("api:gitee:login", args=[tenant_id,])
        callback_url = reverse("api:gitee:callback", args=[tenant_id])
        bind_url = reverse("api:gitee:bind", args=[tenant_id])


        return {
            'client_id': client_id,
            'secret_id': secret_id,
            'login_url': LOGIN_URL,
            'img_url': IMG_URL,
            'login_url': login_url,
            'callback_url': callback_url,
            'bind_url': bind_url,
        }

    def bind(self, user: any, data: Dict):
        from .models import GiteeUser

        GiteeUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            gitee_user_id=data.get("user_id"),
        )

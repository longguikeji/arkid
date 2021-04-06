from typing import Dict
from .user_info_manager import GithubUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, BIND_KEY, LOGIN_URL, IMG_URL


class GithubExternalIdpProvider(ExternalIdpProvider):

    bind_key: str = BIND_KEY
    name: str

    client_id: str
    secret_id: str

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

        self.client_id = client_id
        self.secret_id = secret_id

    def create(self, external_idp, data):
        client_id = data.get('client_id')
        secret_id = data.get('secret_id')

        return {
            'client_id': client_id,
            'secret_id': secret_id,
            'login_url': LOGIN_URL,
            'img_url': IMG_URL,
        }

    def bind(self, user: any, data: Dict):
        from .models import GithubUser

        GithubUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            github_user_id=data.get('user_id'),
        )

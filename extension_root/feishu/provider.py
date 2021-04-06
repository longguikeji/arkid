import requests
from typing import Dict
from runtime import Runtime
from common.extension import InMemExtension
from common.provider import ExternalIdpProvider
from .constants import KEY, GET_TENANT_ACCESS_TOKEN


class FeishuExternalIdpProvider(ExternalIdpProvider):

    app_id: str
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

        app_id = data.get('app_id')
        secret_id = data.get('secret_id')

        self.app_id = app_id
        self.secret_id = secret_id

    def create(self, external_idp, data):
        app_id = data.get('app_id')
        secret_id = data.get('secret_id')

        return {
            'app_id': app_id,
            'secret_id': secret_id,
        }

    def get_groups(self):
        url = 'https://open.feishu.cn/open-apis/contact/v3/departments?parent_department_id=0'
        token = self._get_token()
        r = requests.get(url, headers={
            'Authorization': f'Bearer {token}',
        })
        data = r.json()
        return data

    def get_users(self):
        url = 'https://open.feishu.cn/open-apis/contact/v3/users'
        token = self._get_token()
        r = requests.get(url, headers={
            'Authorization': f'Bearer {token}',
        })
        data = r.json()
        return data

    def _get_token(self):
        '''
        {
            "code":0,
            "msg":"ok",
            "app_access_token":"xxxxx",
            "expire":7200,  // 过期时间，单位为秒（两小时失效）
            "tenant_access_token":"xxxxx"
        }
        '''
        url = GET_TENANT_ACCESS_TOKEN
        r = requests.post(url, data={
            'app_id': self.app_id,
            'app_secret': self.app_secret,
        })
        data = r.json()
        token = data['tenant_access_token']
        return token

    def bind(self, user: any, data: Dict):
        from .models import FeishuUser

        FeishuUser.objects.get_or_create(
            tenant=user.tenant,
            user=user,
            feishu_user_id=data.get("user_id"),
        )

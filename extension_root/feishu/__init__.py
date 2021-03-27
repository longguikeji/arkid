import typing
import requests
from runtime import Runtime
from extension.models import Extension
from common.provider import ExternalIdpProvider


class FeishuExternalIdpProvider(ExternalIdpProvider):

    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret

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
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/'
        r = requests.post(url, data={
            'app_id': self.app_id,
            'app_secret': self.app_secret,
        })
        data = r.json()
        token = data['tenant_access_token']
        return token


class FeishuExtension(Extension):    

    def start(self, runtime: Runtime, *args, **kwargs):
        super().start(runtime, *args, **kwargs)

        provider = FeishuExternalIdpProvider(
            app_id=self.config('app_id'),
            app_secret=self.config('app_secret'),
        )


        runtime.register_external_idp(
            id='feishu',             
            name='飞书',
            description='字节跳动出品的即时沟通工具',
            provider=provider,
        )


extension = FeishuExtension(
    scope='tenant', #TODO: to support tenant isolated extension
    name='feishu',
    description='飞书',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='insfocus@gmail.com',
)

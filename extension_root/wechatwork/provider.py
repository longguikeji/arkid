from typing import Dict
from .user_info_manager import WeChatWorkUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY
from django.urls import reverse
from config import get_app_config


class WeChatWorkExternalIdpProvider(ExternalIdpProvider):

    appid: str
    secret: str
    login_url: str
    bind_url: str
    userinfo_url: str

    def __init__(self) -> None:
        super().__init__()

    def load_data(self, tenant_uuid):
        from tenant.models import Tenant
        from external_idp.models import ExternalIdp
        host = get_app_config().get_host()

        idp = ExternalIdp.active_objects.filter(
            tenant__uuid=tenant_uuid,
            type=KEY,
        ).first()

        assert idp is not None
        data = idp.data

        appid = data.get('appid')
        secret = data.get('secret')
        login_url = data.get('login_url')
        bind_url = data.get('bind_url')
        userinfo_url = data.get('userinfo_url')

        self.appid = appid
        self.secret = secret
        self.bind_url = bind_url
        self.userinfo_url = userinfo_url

    def create(self, tenant_uuid, external_idp, data):
        host = get_app_config().get_host()
        appid = data.get('appid')
        secret = data.get('secret')
        login_url = host+reverse("api:wechatwork:login", args=[tenant_uuid])
        bind_url = host+reverse("api:wechatwork:bind", args=[tenant_uuid])
        userinfo_url = host+reverse("api:wechatwork:userinfo", args=[tenant_uuid])

        return {
            'appid': appid,
            'secret': secret,
            'login_url': login_url,
            'bind_url': bind_url,
            'userinfo_url': userinfo_url,
        }

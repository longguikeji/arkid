from typing import Dict
from .user_info_manager import WeChatWorkUserInfoManager
from common.provider import ExternalIdpProvider
from .constants import KEY, IMG_URL
from django.urls import reverse
from config import get_app_config


class WeChatWorkExternalIdpProvider(ExternalIdpProvider):

    corpid: str
    corpsecret: str
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

        corpid = data.get('corpid')
        corpsecret = data.get('corpsecret')
        bind_url = data.get('bind_url')
        userinfo_url = data.get('userinfo_url')

        self.corpid = corpid
        self.corpsecret = corpsecret
        self.bind_url = bind_url
        self.userinfo_url = userinfo_url

    def create(self, tenant_uuid, external_idp, data):
        host = get_app_config().get_host()
        corpid = data.get('corpid')
        corpsecret = data.get('corpsecret')
        login_url = host+reverse("api:wechatwork:login", args=[tenant_uuid])
        bind_url = host+reverse("api:wechatwork:bind", args=[tenant_uuid])
        userinfo_url = host+reverse("api:wechatwork:userinfo", args=[tenant_uuid])

        return {
            'corpid': corpid,
            'corpsecret': corpsecret,
            'login_url': login_url,
            'bind_url': bind_url,
            'userinfo_url': userinfo_url,
            'img_url': IMG_URL,
        }

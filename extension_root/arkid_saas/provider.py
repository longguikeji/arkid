from common.provider import ExternalIdpProvider
from .constants import KEY
from config import get_app_config

from typing import Dict
from common.provider import AppTypeProvider
from oauth2_provider.models import Application
from django.urls import reverse
from tasks.tasks import by_app_client_id_update_permission


class ArkIDSaasIdpProvider(ExternalIdpProvider):
    def __init__(self) -> None:
        super().__init__()

    def load_data(self, tenant_uuid):
        from external_idp.models import ExternalIdp

        idp = ExternalIdp.active_objects.filter(
            tenant__uuid=tenant_uuid,
            type=KEY,
        ).first()
        assert idp is not None

        data = idp.data
        
        self.scope = 'openid'
        self.client_id = data.get('client_id')
        self.client_secret = data.get('client_secret')
        self.authorize_url = data.get('authorize_url')
        self.token_url = data.get('token_url')
        self.userinfo_url = data.get('userinfo_url')
        self.img_url = data.get('img_url')
        self.login_url = data.get('login_url')
        self.callback_url = data.get('callback_url')
    
    def create(self, data, **kwargs):
        host = get_app_config().get_frontend_host()
        img_url = host + '/favicon.ico'
        return {
            'client_id': data.get('client_id'),
            'client_secret': data.get('client_secret'),
            'authorize_url': data.get('authorize_url'),
            'token_url': data.get('token_url'),
            'userinfo_url': data.get('userinfo_url'),
            'img_url': data.get('img_url', img_url),
            'login_url': data.get('login_url'),
            'callback_url': data.get('callback_url'),
        }


class OAuth2AppTypeProvider(AppTypeProvider):

    def create(self, app, data: Dict) -> Dict:
        '''
        User, Redirect URI, Client Type, Grant Type, Name
        '''

        client_type = data.get('client_type')
        skip_authorization = data.get('skip_authorization')
        redirect_uris = data.get('redirect_uris')
        openapi_uris = data.get('openapi_uris')
        version = data.get('version')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        host = get_app_config().get_host()
        obj = Application()
        obj.name = app.id
        obj.client_type = client_type
        obj.skip_authorization = skip_authorization
        obj.redirect_uris = redirect_uris
        if algorithm:
            obj.algorithm = algorithm
        obj.authorization_grant_type = authorization_grant_type
        obj.save()

        userinfo_url = host+reverse("api:arkid_saas:oauth-user-info-platform")
        authorize_url = host+reverse("api:arkid_saas:authorize-platform")
        token_url = host+reverse("api:arkid_saas:token-platform")

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'openapi_uris': openapi_uris,
            'version': version,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'skip_authorization': obj.skip_authorization,
            'userinfo': userinfo_url,
            'authorize': authorize_url,
            'token':  token_url,
        }
        if algorithm:
            uniformed_data['algorithm'] = obj.algorithm
            uniformed_data['logout'] = host+reverse("api:arkid_saas:oauth-user-logout-platform")

        if openapi_uris != '':
            # 增加逻辑判断更新app的权限
            by_app_client_id_update_permission.delay(obj.client_id)
        return uniformed_data

    def update(self, app, data: Dict) -> Dict:
        client_type = data.get('client_type')
        redirect_uris = data.get('redirect_uris')
        openapi_uris = data.get('openapi_uris')
        version = data.get('version')
        skip_authorization = data.get('skip_authorization')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        host = get_app_config().get_host()
        data_version = app.data.get('version')

        obj = Application.objects.filter(name=app.id).first()
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        obj.skip_authorization = skip_authorization
        obj.authorization_grant_type = authorization_grant_type
        if algorithm:
            obj.algorithm = algorithm
        obj.save()

        userinfo_url = host+reverse("api:arkid_saas:oauth-user-info-platform")
        authorize_url = host+reverse("api:arkid_saas:authorize-platform")
        token_url = host+reverse("api:arkid_saas:token-platform")

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'openapi_uris': openapi_uris,
            'version': version,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'skip_authorization': obj.skip_authorization,
            'userinfo': userinfo_url,
            'authorize': authorize_url,
            'token':  token_url,
        }
        if algorithm:
            uniformed_data['algorithm'] = obj.algorithm
            uniformed_data['logout'] = host+reverse("api:arkid_saas:oauth-user-logout-platform")

        if data_version != version and openapi_uris != '':
            # 增加逻辑判断更新app的权限
            by_app_client_id_update_permission.delay(obj.client_id)
        return uniformed_data

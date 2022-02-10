from typing import Dict
from app.models import App
from common.provider import AppTypeProvider
from oauth2_provider.models import Application
from django.urls import reverse
from config import get_app_config


class OAuth2AppTypeProvider(AppTypeProvider):

    def create(self, app, data: Dict) -> Dict:
        '''
        User, Redirect URI, Client Type, Grant Type, Name
        '''

        client_type = data.get('client_type')
        skip_authorization = data.get('skip_authorization')
        redirect_uris = data.get('redirect_uris')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        is_platform = data.get('is_platform')
        host = get_app_config().get_host()
        obj = Application()
        obj.name = app.id
        obj.client_type = client_type
        obj.skip_authorization = skip_authorization
        obj.redirect_uris = redirect_uris
        if algorithm and app.type == 'OIDC':
            obj.algorithm = algorithm
        obj.authorization_grant_type = authorization_grant_type
        obj.is_platform = is_platform
        obj.save()

        if is_platform:
            userinfo_url = host+reverse("api:oauth2_authorization_server:oauth-user-info-platform")
            authorize_url = host+reverse("api:oauth2_authorization_server:authorize-platform")
            token_url = host+reverse("api:oauth2_authorization_server:token-platform")
        else:
            # userinfo_url = host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[app.tenant.uuid])
            # authorize_url = host+reverse("api:oauth2_authorization_server:authorize", args=[app.tenant.uuid])
            # token_url = host+reverse("api:oauth2_authorization_server:token", args=[app.tenant.uuid])
            tenan_uuid = str(app.tenant.uuid)
            authorize_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/authorize/"
            token_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/token/"
            userinfo_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/userinfo/"

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'skip_authorization': obj.skip_authorization,
            'is_platform': is_platform,
            'userinfo': userinfo_url,
            'authorize': authorize_url,
            'token':  token_url,
        }
        if algorithm and app.type == 'OIDC':
            uniformed_data['algorithm'] = obj.algorithm
            if is_platform:
                uniformed_data['logout'] = host+reverse("api:oauth2_authorization_server:oauth-user-logout-platform")
            else:
                # uniformed_data['logout'] = host+reverse("api:oauth2_authorization_server:oauth-user-logout", args=[app.tenant.uuid])
                tenan_uuid = str(app.tenant.uuid)
                userinfo_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/logout/"
        return uniformed_data

    def update(self, app, data: Dict) -> Dict:
        client_type = data.get('client_type')
        redirect_uris = data.get('redirect_uris')
        skip_authorization = data.get('skip_authorization')
        authorization_grant_type = data.get('grant_type')
        is_platform = data.get('is_platform')
        algorithm = data.get('algorithm')
        host = get_app_config().get_host()
        obj = Application.objects.filter(name=app.id).first()
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        obj.skip_authorization = skip_authorization
        obj.authorization_grant_type = authorization_grant_type
        obj.is_platform = is_platform
        if algorithm and app.type == 'OIDC':
            obj.algorithm = algorithm
        obj.save()

        if is_platform:
            userinfo_url = host+reverse("api:oauth2_authorization_server:oauth-user-info-platform")
            authorize_url = host+reverse("api:oauth2_authorization_server:authorize-platform")
            token_url = host+reverse("api:oauth2_authorization_server:token-platform")
        else:
            # reverse tenan_urls not working 
            # userinfo_url = host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[app.tenant.uuid])
            # authorize_url = host+reverse("api:oauth2_authorization_server:authorize", args=[app.tenant.uuid])
            # token_url = host+reverse("api:oauth2_authorization_server:token", args=[app.tenant.uuid])
            tenan_uuid = str(app.tenant.uuid)
            authorize_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/authorize/"
            token_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/token/"
            userinfo_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/userinfo/"

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'skip_authorization': obj.skip_authorization,
            'is_platform': is_platform,
            'userinfo': userinfo_url,
            'authorize': authorize_url,
            'token':  token_url,
        }
        if algorithm and app.type == 'OIDC':
            uniformed_data['algorithm'] = obj.algorithm
            if is_platform:
                uniformed_data['logout'] = host+reverse("api:oauth2_authorization_server:oauth-user-logout-platform")
            else:
                # uniformed_data['logout'] = host+reverse("api:oauth2_authorization_server:oidc/logout/", args=[app.tenant.uuid])
                tenan_uuid = str(app.tenant.uuid)
                userinfo_url = f"{host}/api/v1/tenant/{tenan_uuid}/oauth/logout/"
        return uniformed_data

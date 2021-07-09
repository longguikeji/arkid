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
        redirect_uris = data.get('redirect_uris')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        host = get_app_config().get_host()
        obj = Application()
        obj.name = app.id
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        if algorithm and app.type == 'OIDC':
            obj.algorithm = algorithm
        obj.authorization_grant_type = authorization_grant_type
        obj.save()

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'userinfo': host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[app.tenant.uuid]),
            'authorize': host+reverse("api:oauth2_authorization_server:authorize", args=[app.tenant.uuid]),
            'token': host+reverse("api:oauth2_authorization_server:token", args=[app.tenant.uuid]),
        }
        if algorithm and app.type == 'OIDC':
            uniformed_data['algorithm'] = obj.algorithm
        return uniformed_data

    def update(self, app, data: Dict) -> Dict:
        client_type = data.get('client_type')
        redirect_uris = data.get('redirect_uris')
        authorization_grant_type = data.get('grant_type')
        algorithm = data.get('algorithm')
        host = get_app_config().get_host()
        obj = Application.objects.filter(name=app.id).first()
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        obj.authorization_grant_type = authorization_grant_type
        if algorithm and app.type == 'OIDC':
            obj.algorithm = algorithm
        obj.save()
        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'userinfo': host+reverse("api:oauth2_authorization_server:oauth-user-info", args=[app.tenant.uuid]),
            'authorize': host+reverse("api:oauth2_authorization_server:authorize", args=[app.tenant.uuid]),
            'token': host+reverse("api:oauth2_authorization_server:token", args=[app.tenant.uuid]),
        }
        if algorithm and app.type == 'OIDC':
            uniformed_data['algorithm'] = obj.algorithm
        return uniformed_data

from typing import Dict
from app.models import App
from common.provider import AppTypeProvider
from django.urls import reverse


class OAuth2AppTypeProvider(AppTypeProvider):

    def create(self, app, data: Dict) -> Dict:
        from oauth2_provider.models import Application

        '''
        User, Redirect URI, Client Type, Grant Type, Name
        '''

        client_type = data.get('client_type')
        redirect_uris = data.get('redirect_uris')
        authorization_grant_type = data.get('grant_type')
        
        obj = Application()
        obj.name = app.id
        obj.client_type = client_type
        obj.redirect_uris = redirect_uris
        obj.authorization_grant_type = authorization_grant_type
        obj.save()

        uniformed_data = {
            'client_type': client_type,
            'redirect_uris': redirect_uris,
            'grant_type': authorization_grant_type,
            'client_id': obj.client_id,
            'client_secret': obj.client_secret,
            'authorize': reverse("api:oauth2_authorization_server:authorize", args=[app.tenant.uuid]),
            'token': reverse("api:oauth2_authorization_server:token", args=[app.tenant.uuid]),
        }

        return uniformed_data
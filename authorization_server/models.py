from typing import (
    Optional
)

from django.utils.translation import gettext_lazy as _
from common.provider import AuthorizationServerProvider


class AuthorizationServer:

    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    provider: Optional[AuthorizationServerProvider] = None

    def __init__(self, id: str, name: str, description: str='', provider: AuthorizationServerProvider=None) -> None:
        self.id = id
        self.name = name 
        self.description = description
        self.provider = provider

    

class OAuthAuthorizationServer(AuthorizationServer):

    @property
    def app_settings_sehema(self):
        return [
            {
                "key": "redirect_url",
                "name": "Redirect URL",
                "type": "string",
            },
            {
                "key": "grant",
                "name": "Grant",
                "type": "array",
                "value": [
                    {"name": _("Authorization code"), "value": "authorization-code"}, 
                    {"name": _("Implicit"), "value": "implicit"}, 
                    {"name": _("Resource owner password-based"), "value": "password"}, 
                    {"name": _("Client credentials"), "value": "client-credentials"}
                ],
            }
        ]
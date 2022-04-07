import functools
from ninja import NinjaAPI
from ninja.security import HttpBearer
from django.conf import settings

# from .models import User
from arkid.core.openapi import get_openapi_schema
# from .utils import verify_id_token


class GlobalAuth(HttpBearer):
    openapi_scheme = "token"

    def authenticate(self, request, token):
        try:
            user_info = verify_id_token(token, client_id, oauth_url)
            user = User.objects.get(user_uuid=user_info["sub_uuid"])
        except:
            return

        request.user = user
        return token


api = NinjaAPI(auth=GlobalAuth())

api.get_openapi_schema = functools.partial(get_openapi_schema, api)

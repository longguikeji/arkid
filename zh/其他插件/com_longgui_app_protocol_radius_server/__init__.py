from django.urls import reverse
from django.conf import settings
from arkid.core.api import operation
from django.http import JsonResponse
from arkid.core.extension import Extension
from arkid.core.token import get_valid_token
from arkid.extension.models import TenantExtension
from arkid.core.extension import create_extension_schema
from django.contrib.auth.hashers import check_password
from arkid.core.constants import *
from .schema import *
from .error import ErrorCode

RadiusServerSchema = create_extension_schema('RadiusServerSchema', __file__, base_schema=RadiusServerBaseSchema)

class RadiusServerExtension(Extension):

    def load(self):
        self.register_settings_schema(RadiusServerSchema)
        super().load()
        self.register_api('/radius_login/', 'POST', (self.radius_login), tenant_path=True, auth=None)

    def radius_login(self, request, tenant_id: str, data: RadiusLoginSchemaIn):
        from arkid.core.models import User

        username = data.username
        password = data.password
        tenant = request.tenant

        #  Code   Meaning       Process body  Module code
        #  404    not found     no            notfound
        #  410    gone          no            notfound
        #  403    forbidden     no            userlock
        #  401    unauthorized  yes           reject
        #  204    no content    no            ok
        #  2xx    successful    yes           ok/updated
        #  5xx    server error  no            fail
        #  xxx    -             no            invalid
        user = tenant.users.filter(is_del=False).filter(username=username).first()
        if user:
            user = User.expand_objects.filter(id=user.id).first()
            user_password = user.get("password")
            if user_password and check_password(password, user_password):
                return JsonResponse(data={}, status=200)
            else:
                return JsonResponse(data={}, status=401)
        else:
            return JsonResponse(data={}, status=401)


extension = RadiusServerExtension()
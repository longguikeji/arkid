from django.urls import reverse
from django.conf import settings
from arkid.core.api import operation
from arkid.core.extension import Extension
from arkid.core.token import get_valid_token
from arkid.extension.models import TenantExtension
from arkid.core.extension import create_extension_schema
from arkid.core.constants import *
from .schema import *
from .error import ErrorCode
from .client import RADIUSBackend

RadiusClientSchema = create_extension_schema('RadiusClientSchema', __file__, base_schema=RadiusClientBaseSchema)

class RadiusClientExtension(Extension):

    def load(self):
        self.register_settings_schema(RadiusClientSchema)
        super().load()
        self.register_api('/radius_login/', 'POST', (self.radius_login), tenant_path=True, auth=None)

    def radius_login(self, request, tenant_id: str, data: RadiusLoginSchemaIn):
        username = data.username
        password = data.password
        server = ''
        port = ''
        secret = ''
        extension = self.model
        te = TenantExtension.valid_objects.filter(tenant_id=tenant_id,
          extension_id=(extension.id)).first()
        if te:
            server = te.settings.get('server', '')
            port = te.settings.get('port', '')
            secret = te.settings.get('secret', '')
        if server:
            radius_client = RADIUSBackend(server, port, secret)
            user = radius_client.authenticate(request, username, password)
            if user:
                token = get_valid_token(user, request.tenant)
                return self.success({'token': str(user.auth_token)})
            else:
                return self.error(ErrorCode.LOGIN_FAILURE)
        else:
            return self.error(ErrorCode.NOT_CONFIG)


extension = RadiusClientExtension()
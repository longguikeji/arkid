#!/usr/bin/env python3

from arkid.core.extension.auto_auth import AutoAuthExtension
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension
import urllib.parse
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from django.http.response import JsonResponse, HttpResponse
from .exception import GSSServerInitError, GSSServerStepError
from arkid.common.logger import logger
from arkid.core.models import User
from arkid.core.token import refresh_token

class KerberosLoginConfigSchema(Schema):
    service_principal: str = Field(
        title=_('Service Principal', 'Kerberos服务主体'), default=''
    )


KerberosLoginConfigSchema = create_extension_schema(
    'KerberosLoginConfigSchema', __file__, base_schema=KerberosLoginConfigSchema
)


class AutoAuthKerberosExtension(AutoAuthExtension):
    def load(self):
        super().load()
        self.register_auto_auth_schema(KerberosLoginConfigSchema, 'kerberos')

    def challenge(self, request, *args, **kwargs):
        '''Send negotiate challenge'''
        response = HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Negotiate'
        return response

    def authenticate(self, event, **kwargs):
        import kerberos

        tenant = event.tenant
        request = event.request
        extension_config = self.get_tenant_configs(tenant).first()

        if not extension_config or not extension_config.config:
            return None
        config = extension_config.config

        if 'HTTP_AUTHORIZATION' in request.META:
            kind, authstr = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if kind == 'Negotiate':
                try:
                    context = None
                    service = config.get('service_principal')
                    logger.info(u'using service name %s', service)
                    logger.debug(u'Negotiate authstr %r', authstr)
                    rc, context = kerberos.authGSSServerInit(service)
                    if rc != kerberos.AUTH_GSS_COMPLETE:
                        raise GSSServerInitError()
                    rc = kerberos.authGSSServerStep(context, authstr)
                    if rc != kerberos.AUTH_GSS_COMPLETE:
                        raise GSSServerStepError()
                    gss_key = kerberos.authGSSServerResponse(context)

                    fulluser = kerberos.authGSSServerUserName(context)
                    user_name = fulluser.split("@", 1)[0]

                except kerberos.GSSError as e:
                    return None
                finally:
                    if context is not None:
                        kerberos.authGSSServerClean(context)

                user = self.get_user(user_name, tenant)
                # response = self.get_response(user, gss_key)
                return user
        return self.challenge(request)

    def get_user(self, user_name, tenant):
        user, created = User.valid_objects.get_or_create(
            username=user_name, tenant=tenant
        )
        return user

    def get_response(self, user, gss_key):
        token = refresh_token(user)
        response = JsonResponse({'token': token})
        response['WWW-Authenticate'] = 'Negotiate %s' % gss_key
        return response


extension = AutoAuthKerberosExtension()
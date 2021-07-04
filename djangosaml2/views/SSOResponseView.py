from django.views import View
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache

from saml2 import BINDING_HTTP_POST, saml
from saml2.authn_context import PASSWORD, AuthnBroker, authn_context_class_ref
from saml2.md import entity_descriptor_from_string
from saml2.ident import NameID

from app.models import App
from django.core.exceptions import ImproperlyConfigured, PermissionDenied

@method_decorator(never_cache, name='dispatch')
class SSOResponse(View):
    """
    阿里云角色SSO登录
    """
    CUSTOM_CONFIG = {
        'role': 'https://www.aliyun.com/SAML-Role/Attributes/Role',
        'role_session_name': 'https://www.aliyun.com/SAML-Role/Attributes/RoleSessionName',
        'session_duration': 'https://www.aliyun.com/SAML-Role/Attributes/SessionDuration',
    }

    def cookie_user(self, request):    # pylint: disable=no-self-use
        """
        返回cookie对应的用户
        """
        try:
            spauthn = request.COOKIES['spauthn']
            token = ExpiringToken.objects.get(key=spauthn)
            return token.user
        except Exception:    # pylint: disable=broad-except
            return request.user


    def get(self, request, tenant_uuid, app_id, *args, **kwargs):    # pylint: disable=missing-function-docstring, unused-argument, too-many-locals 
        app = App.active_objects.get(id=app_id)
        resp_args = {
            'in_response_to': app.data["acs"],
            'sp_entity_id': app.data["entity_id"],
            'name_id_policy': saml.NAMEID_FORMAT_PERSISTENT,
            'binding': BINDING_HTTP_POST,
            'destination': app.data["acs"],
        }
        sp_config = {
            'processor': 'djangosaml2.processors.BaseProcessor',
            'attribute_mapping': {
                'username': 'username',
                'token': 'token',
                'aliyun_sso_roles': self.CUSTOM_CONFIG['role'],
                'uid': self.CUSTOM_CONFIG['role_session_name'],
                'aliyun_sso_session_duration': self.CUSTOM_CONFIG['session_duration'],
            },
        }
        processor = self.get_processor(resp_args['sp_entity_id'], sp_config)
        # Check if user has access to the service of this SP
        if not processor.has_access(request):
            return self.handle_error(
                request,
                exception=PermissionDenied(
                    "You do not have access to this resource"
                ),
                status=403
            )
        cookie_user = self.cookie_user(request)
        if not cookie_user.aliyun_sso_role.is_active:
            # 用户的角色SSO被禁用
            return self.handle_error(request, exception=PermissionDenied("Your role SSO has been disabled"), status=403)
        identity = self.get_identity(processor, cookie_user, sp_config)
        # print('identity is', identity)
        AUTHN_BROKER = AuthnBroker()    # pylint: disable=invalid-name
        AUTHN_BROKER.add(authn_context_class_ref(PASSWORD), "")
        user_id = processor.get_user_id(cookie_user)
        # Construct SamlResponse message
        try:
            _spsso_descriptor = entity_descriptor_from_string(
                app.data["xmldata"]
            ).spsso_descriptor.pop()    # pylint: disable=no-member
            authn_resp = self.IDP.create_authn_response(
                identity=identity,
                userid=user_id,
                name_id=NameID(
                    format=resp_args['name_id_policy'],
                    sp_name_qualifier=resp_args['sp_entity_id'],
                    text=user_id
                ),
                authn=AUTHN_BROKER.get_authn_by_accr(
                    PASSWORD
                ),
                sign_response=getattr(
                    _spsso_descriptor,
                    'want_response_signed',
                    ''
                ) == 'true',
                sign_assertion=getattr(
                    _spsso_descriptor,
                    'want_assertions_signed',
                    ''
                ) == 'true',
                **resp_args
            )
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)
        # print('authn_resp is', authn_resp)
        http_args = self.IDP.apply_binding(
            binding=resp_args['binding'],
            msg_str="%s" % authn_resp,
            destination=resp_args['destination'],
            response=True
        )
        return HttpResponse(http_args['data'])
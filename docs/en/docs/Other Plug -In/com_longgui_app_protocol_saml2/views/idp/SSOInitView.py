"""
SAML2.0
"""
import logging
from typing import Dict, List, Union
from django.core.exceptions import PermissionDenied
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from saml2.authn_context import AuthnBroker, PASSWORD, authn_context_class_ref
from saml2.saml import NAMEID_FORMAT_UNSPECIFIED, NameID
from ...mxins import IdPHandlerViewMixin, LoginRequiredMixin
from ...idp import IDP
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from saml2.md import entity_descriptor_from_string
logger = logging.getLogger(__name__)


@method_decorator(never_cache, name='dispatch')
class SSOInit(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View used for IDP initialized login, doesn't handle any SAML authn request
    """

    def post(self, request: HttpRequest, tenant_id, config_id, *args, **kwargs) -> HttpResponse:
        """
        POST 方法
        """
        return self.get(request, tenant_id, config_id, *args, **kwargs)

    def get(self, request: HttpRequest, tenant_id, config_id, *args, **kwargs) -> HttpResponse:
        """
        GET方法
        """
        sp_entity_id = self.config.config.get("entity_id")

        sp_config = {
            'attribute_mapping': {
                'username': 'username',
                'email': 'email',
                'name': 'first_name',
                'is_boss': 'is_admin',
                'token': 'token',
            },
            'extra_config': self.config.config.get("attribute_mapping", {}) 
        }

        idp_server = self.IDP

        binding_out, destination = idp_server.pick_binding(
            service="assertion_consumer_service",
            entity_id=sp_entity_id
        )

        # Adding a few things that would have been added if this were SP Initiated
        processor = self.get_processor(sp_entity_id, sp_config)

        # Check if user has access to the service of this SP
        if not processor.has_access(request):
            return self.handle_error(
                request,
                exception=PermissionDenied(
                    "You do not have access to this resource"
                ),
                status=403
            )

        identity = self.get_identity(processor, request.user, sp_config)

        req_authn_context = PASSWORD
        AUTHN_BROKER = AuthnBroker()    # pylint: disable=invalid-name
        AUTHN_BROKER.add(authn_context_class_ref(req_authn_context), "")

        user_id = processor.get_user_id(request.user)

        # Construct SamlResponse messages
        try:
            name_id_formats = self.IDP.config.getattr("name_id_format", "idp") or [
                NAMEID_FORMAT_UNSPECIFIED
            ]
            
            if self.config.config.get("type",None)=="Saml2SP_AliyunRam":
                user_id = f"{user_id}@{self.config.config.get('auxiliary_domain')}"
            
            name_id = NameID(format=name_id_formats[0], text=user_id)
            authn = AUTHN_BROKER.get_authn_by_accr(req_authn_context)
            sign_response = True
            sign_assertion = True
            authn_resp = self.IDP.create_authn_response(
                identity=identity,
                in_response_to=None,
                destination=destination,
                sp_entity_id=sp_entity_id,
                userid=user_id,
                name_id=name_id,
                authn=authn,
                sign_response=sign_response,
                sign_assertion=sign_assertion,
            )
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)

        # Return as html with self-submitting form.
        http_args = self.IDP.apply_binding(
            binding=binding_out,
            msg_str="%s" % authn_resp,
            destination=destination,
            response=True
        )
        return HttpResponse(http_args['data'])
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
from djangosaml2idp.mxins import IdPHandlerViewMixin, LoginRequiredMixin
from djangosaml2idp.idp import IDP
from app.models import App


logger = logging.getLogger(__name__)


@method_decorator(never_cache, name='dispatch')
class SSOInit(LoginRequiredMixin, IdPHandlerViewMixin, View):
    """ View used for IDP initialized login, doesn't handle any SAML authn request
    """

    def post(self, request: HttpRequest, tenant__uuid, app_id, *args, **kwargs) -> HttpResponse:
        """
        POST 方法
        """
        return self.get(request, tenant__uuid, app_id, *args, **kwargs)

    def get(self, request: HttpRequest, tenant__uuid, app_id, *args, **kwargs) -> HttpResponse:
        """
        GET方法
        """
        request_data = request.POST or request.GET
        passed_data: Dict[
            str,
            Union[
                str,
                List[str]
            ]
        ] = request_data.copy().dict()

        # TODO 鉴权

        app = App.objects.get(id=app_id)
        sp_entity_id = app.data.get("entity_id")

        sp_config = {
            'processor': 'djangosaml2idp.processors.BaseProcessor',
            'attribute_mapping': {
                'username': 'username',
                'email': 'email',
                'name': 'first_name',
                'is_boss': 'is_admin',
                'token': 'token',
            },
            'extra_config': app.data["attribute_mapping"]
        }

        idp_server = IDP.load(tenant__uuid, app_id)

        binding_out, destination = idp_server.pick_binding(
            service="assertion_consumer_service",
            entity_id=sp_entity_id)

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
            name_id = NameID(format=name_id_formats[0], text=user_id)
            authn = AUTHN_BROKER.get_authn_by_accr(req_authn_context)
            sign_response = self.IDP.config.getattr(
                "sign_response", "idp"
            ) or True
            sign_assertion = self.IDP.config.getattr(
                "sign_assertion", "idp"
            ) or True
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
                **passed_data
            )
        except Exception as excp:    # pylint: disable=broad-except
            return self.handle_error(request, exception=excp, status=500)

        # Return as html with self-submitting form.
        http_args = self.IDP.apply_binding(
            binding=binding_out,
            msg_str="%s" % authn_resp,
            destination=destination,
            relay_state=passed_data.get('RelayState',None),
            response=True
        )
        return HttpResponse(http_args['data'])

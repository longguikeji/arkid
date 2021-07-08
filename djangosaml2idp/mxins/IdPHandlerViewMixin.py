from typing import Optional
import base64
import logging

from django.template.loader import get_template
from django.template.exceptions import (TemplateDoesNotExist,TemplateSyntaxError)
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.backends.django import Template
from django.urls import reverse

from saml2 import BINDING_HTTP_POST
from djangosaml2idp.processors import BaseProcessor

logger = logging.getLogger(__name__)

class IdPHandlerViewMixin:
    """ Contains some methods used by multiple views """

    def render_login_html_to_string(self, context=None, request=None, using=None):
        """ Render the html response for the login action. Can be using a custom html template if set on the view. """
        default_login_template_name = 'djangosaml2idp/login.html'
        custom_login_template_name = getattr(self, 'login_html_template', None)

        if custom_login_template_name:
            template = self._fetch_custom_template(custom_login_template_name, default_login_template_name, using)
            return template.render(context, request)

        template = get_template(default_login_template_name, using=using)
        return template.render(context, request)

    @staticmethod
    def _fetch_custom_template(custom_name: str, default_name: str, using: Optional[str] = None) -> Template:
        """ Grabs the custom login template. Falls back to default if issues arise. """
        try:
            template = get_template(custom_name, using=using)
        except (TemplateDoesNotExist, TemplateSyntaxError) as e:
            logger.error(
                'Specified template {} cannot be used due to: {}. Falling back to default login template {}'.format(
                    custom_name, str(e), default_name))
            template = get_template(default_name, using=using)
        return template

    def create_html_response(self, request: HttpRequest, binding, authn_resp, destination, relay_state):
        """ Login form for SSO
        """
        if binding == BINDING_HTTP_POST:
            context = {
                "acs_url": destination,
                "saml_response": base64.b64encode(str(authn_resp).encode()).decode(),
                "relay_state": relay_state,
            }
            html_response = {
                "data": self.render_login_html_to_string(context=context, request=request),
                "type": "POST",
            }
        else:
            idp_server = IDP.load()
            http_args = idp_server.apply_binding(
                binding=binding,
                msg_str=authn_resp,
                destination=destination,
                relay_state=relay_state,
                response=True)

            logger.debug('http args are: %s' % http_args)
            html_response = {
                "data": http_args['headers'][0][1],
                "type": "REDIRECT",
            }
        return html_response

    def render_response(self, request: HttpRequest, html_response, processor: BaseProcessor = None) -> HttpResponse:
        """ Return either a response as redirect to MultiFactorView or as html with self-submitting form to log in.
        """
        if not processor:
            # In case of SLO, where processor isn't relevant
            if html_response['type'] == 'POST':
                return HttpResponse(html_response['data'])
            else:
                return HttpResponseRedirect(html_response['data'])

        request.session['saml_data'] = html_response

        if processor.enable_multifactor(request.user):
            logger.debug("Redirecting to process_multi_factor")
            return HttpResponseRedirect(reverse('djangosaml2idp:saml_multi_factor'))

        # No multifactor
        logger.debug("Performing SAML redirect")
        if html_response['type'] == 'POST':
            return HttpResponse(html_response['data'])
        else:
            return HttpResponseRedirect(html_response['data'])
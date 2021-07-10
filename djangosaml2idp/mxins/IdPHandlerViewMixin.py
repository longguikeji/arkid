import copy
from django.utils.module_loading import import_string

from saml2.server import Server
from djangosaml2idp import idpsettings
from saml2.config import IdPConfig
import djangosaml2idp
from djangosaml2idp.idp import IDP
from typing import Optional
import base64
import logging

from django.template.loader import get_template
from django.template.exceptions import (
    TemplateDoesNotExist, TemplateSyntaxError)
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.backends.django import Template
from django.urls import reverse

from saml2 import BINDING_HTTP_POST
from djangosaml2idp.processors import BaseProcessor
from djangosaml2idp.views import SAML2IDPError as error_cbv

logger = logging.getLogger(__name__)


class IdPHandlerViewMixin:
    """ Contains some methods used by multiple views """

    def handle_error(self, request, **kwargs):    # pylint: disable=missing-function-docstring
        return error_cbv.as_view()(request, **kwargs)

    def dispatch(self, request, tenant__uuid, app_id, *args, **kwargs):
        """
        Construct IDP server with config from settings dict
        """
        conf = IdPConfig()
        try:

            conf.load(
                copy.copy(idpsettings.get_saml_idp_config(tenant__uuid, app_id)))
            self.IDP = Server(config=conf)    # pylint: disable=invalid-name
        except Exception as e:    # pylint: disable=invalid-name, broad-except
            return self.handle_error(request, exception=e)
        return super(IdPHandlerViewMixin, self).dispatch(request, tenant__uuid, app_id, *args, **kwargs)

    def get_processor(self, entity_id, sp_config):    # pylint: disable=no-self-use
        """
        Instantiate user-specified processor or default to an all-access base processor.
        Raises an exception if the configured processor class can not be found or initialized.
        """
        processor_string = sp_config.get('processor', None)
        if processor_string:
            try:
                return import_string(processor_string)(entity_id)
            except Exception as e:    # pylint: disable=invalid-name
                logger.error("Failed to instantiate processor: {} - {}".format(processor_string,
                             e), exc_info=True)    # pylint: disable=logging-format-interpolation
                raise
        return BaseProcessor(entity_id)

    def get_identity(self, processor, user, sp_config):    # pylint: disable=no-self-use
        """
        Create Identity dict (using SP-specific mapping)
        """
        sp_mapping = sp_config.get('attribute_mapping', {
                                   'username': 'username'})
        ret = processor.create_identity(
            user, sp_mapping, **sp_config.get('extra_config', {}))
        return ret

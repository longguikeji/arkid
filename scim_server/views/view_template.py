#!/usr/bin/env python3

from cmath import log
import json
import logging
from django.views.generic import View
from scim_server.exceptions import BadRequestException, SCIMException
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from scim_server.protocol.protocol_constants import ProtocolConstants
from scim_server.utils import try_get_request_identifier
from scim_server.service.resource_query import ResourceQuery
from scim_server.protocol.patch_request2 import PatchRequest2
from scim_server.schemas.schema_identifiers import SchemaIdentifiers

logger = logging.getLogger(__name__)


class ViewTemplate(View):
    lookup_url_kwarg = 'uuid'  # argument in django URL pattern

    @property
    def model_cls(self):
        raise NotImplementedError

    # @property
    # def provider(self):
    #     raise NotImplementedError

    @property
    def adapter_provider(self):
        raise NotImplementedError

    def get(self, request, *args, **kwargs):
        correlation_identifier = try_get_request_identifier()
        identifier = self.kwargs.get(self.lookup_url_kwarg, None)
        resource_query = ResourceQuery.initialize(request)
        if identifier:
            result = self.adapter_provider.retrieve(
                request,
                identifier,
                resource_query.attributes,
                resource_query.excluded_attributes,
                correlation_identifier,
            )
            d = result.to_dict()
            return JsonResponse(d)

        else:
            result = self.adapter_provider.query(
                request,
                resource_query.filters,
                resource_query.attributes,
                resource_query.excluded_attributes,
                resource_query.pagination_parameters,
                correlation_identifier,
            )
            d = result.dict()
            return JsonResponse(d)

    def delete(self, request, *args, **kwargs):
        correlation_identifier = try_get_request_identifier()
        identifier = self.kwargs.get(self.lookup_url_kwarg, None)
        if not identifier:
            raise BadRequestException('empty identifier')
        self.adapter_provider.delete(request, identifier, correlation_identifier)
        return HttpResponse(status=204)

    def post(self, request, *args, **kwargs):
        body = request.body
        try:
            d = json.loads(body)
            resource = self.model_cls(**d)
        except Exception as e:
            logger.exception(e)
            raise BadRequestException()

        correlation_identifier = try_get_request_identifier()
        result = self.adapter_provider.create(request, resource, correlation_identifier)
        return JsonResponse(d, status=201)

    def put(self, request, *args, **kwargs):
        correlation_identifier = try_get_request_identifier()
        identifier = self.kwargs.get(self.lookup_url_kwarg, None)
        if not identifier:
            raise BadRequestException('empty identifier')
        body = request.body
        try:
            d = json.loads(body)
            resource = self.model_cls.from_dict(d)
        except Exception as e:
            raise BadRequestException()
        result = self.adapter_provider.replace(request, resource, correlation_identifier)
        return HttpResponse(result)

    def patch(self, request, *args, **kwargs):
        correlation_identifier = try_get_request_identifier()
        identifier = self.kwargs.get(self.lookup_url_kwarg, None)
        if not identifier:
            raise BadRequestException('empty identifier')
        body = request.body
        try:
            d = json.loads(body)
            patch_request = PatchRequest2.from_dict(d)
        except Exception as e:
            raise BadRequestException()
        self.adapter_provider.update(
            request, identifier, patch_request, correlation_identifier
        )
        if (
            self.adapter_provider.schema_identifier
            == SchemaIdentifiers.Core2EnterpriseUser
        ):
            return self.get(request)
        else:
            return HttpResponse(status=204)

    @method_decorator(csrf_exempt)
    # @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # if not self.implemented:
        #     return self.status_501(request, *args, **kwargs)

        try:
            return super().dispatch(request, *args, **kwargs)
        except Exception as e:
            if not isinstance(e, SCIMException):
                logger.exception('Unable to complete SCIM call.')
                e = SCIMException(str(e))

            content = json.dumps(e.to_dict())
            return HttpResponse(
                content=content,
                content_type=ProtocolConstants.ContentType,
                status=e.status,
            )

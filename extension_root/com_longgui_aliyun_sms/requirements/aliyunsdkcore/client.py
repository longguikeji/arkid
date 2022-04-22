# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# coding=utf-8
import os
import sys
import http.client as httplib
import warnings
warnings.filterwarnings("once", category=DeprecationWarning)

try:
    import json
except ImportError:
    import simplejson as json

from .profile import region_provider
from .profile.location_service import LocationService
from .acs_exception.exceptions import ClientException
from .acs_exception.exceptions import ServerException
from .acs_exception import error_code, error_msg
from .http_service.http_response import HttpResponse
from .request import AcsRequest

"""
Acs default client module.

Created on 9/19/2017

@author: guangyao
"""


class AcsClient:
    def __init__(self, ak, secret, region_id, auto_retry=True, max_retry_time=3, user_agent=None, port=80):
        """
        constructor for AcsClient
        :param ak: String, access key id
        :param secret: String, access key secret
        :param region_id: String, region id
        :param auto_retry: Boolean
        :param max_retry_time: Number
        :return:
        """
        self.__max_retry_num = max_retry_time
        self.__auto_retry = auto_retry
        self.__ak = ak
        self.__secret = secret
        self.__region_id = region_id
        self.__user_agent = user_agent
        self._port = port
        self._location_service = LocationService(self)
        self._url_test_flag = False # if true, do_action() will throw a ClientException that contains URL

    def get_region_id(self):
        """

        :return: String
        """
        return self.__region_id

    def get_access_key(self):
        """

        :return: String
        """
        return self.__ak

    def get_access_secret(self):
        """

        :return: String
        """
        return self.__secret

    def is_auto_retry(self):
        """

        :return:Boolean
        """
        return self.__auto_retry

    def get_max_retry_num(self):
        """

        :return: Number
        """
        return self.__max_retry_num

    def get_user_agent(self):
        return self.__user_agent

    def set_region_id(self, region):
        self.__region_id = region

    def set_access_key(self, ak):
        self.__ak = ak

    def set_access_secret(self, secret):
        self.__secret = secret

    def set_max_retry_num(self, num):
        """
        set auto retry number
        :param num: Numbers
        :return: None
        """
        self.__max_retry_num = num

    def set_auto_retry(self, flag):
        """
        set whether or not the client perform auto-retry
        :param flag: Booleans
        :return: None
        """
        self.__auto_retry = flag

    def set_user_agent(self, agent):
        """
        User agent set to client will overwrite the request setting.
        :param agent:
        :return:
        """
        self.__user_agent = agent

    def get_location_service(self):
        return self._location_service

    def get_port(self):
        return self._port

    def _resolve_endpoint(self, request):
        endpoint = None
        if request.get_location_service_code() is not None:
            endpoint = self._location_service.find_product_domain(self.get_region_id(), request.get_location_service_code())
        if endpoint is None:
            endpoint = region_provider.find_product_domain(self.get_region_id(), request.get_product())
            if endpoint is None:
                raise ClientException(error_code.SDK_INVALID_REGION_ID, error_msg.get_msg('SDK_INVALID_REGION_ID'))
            if not isinstance(request, AcsRequest):
                raise ClientException(error_code.SDK_INVALID_REQUEST, error_msg.get_msg('SDK_INVALID_REQUEST'))
        return endpoint

    def _make_http_response(self, endpoint, request):
        content = request.get_content()
        method = request.get_method()
        header = request.get_signed_header(self.get_region_id(), self.get_access_key(),
                                               self.get_access_secret())
        if self.get_user_agent() is not None:
            header['User-Agent'] = self.get_user_agent()
            header['x-sdk-client'] = 'python/2.0.0'
        if header is None:
            header = {}

        protocol = request.get_protocol_type()
        url = request.get_url(self.get_region_id(), self.get_access_key(), self.get_access_secret())
        response = HttpResponse(endpoint, url, method, header, protocol, content,
                                self._port)
        return response

    def _implementation_of_do_action(self, request):
        endpoint = self._resolve_endpoint(request)
        http_response = self._make_http_response(endpoint, request)
        if self._url_test_flag:
            raise ClientException("URLTestFlagIsSet", http_response.get_url())

        # Do the actual network thing
        try:
            status, headers, body = http_response.get_response_object()
            return status, headers, body
        except IOError as e:
            raise ClientException(error_code.SDK_SERVER_UNREACHABLE, error_msg.get_msg('SDK_SERVER_UNREACHABLE') + ': ' + str(e))
        except AttributeError:
            raise ClientException(error_code.SDK_INVALID_REQUEST, error_msg.get_msg('SDK_INVALID_REQUEST'))

    def _parse_error_info_from_response_body(self, response_body):
        try:
            body_obj = json.loads(response_body)
            if 'Code' in body_obj and 'Message' in body_obj:
                return (body_obj['Code'], body_obj['Message'])
            else:
                return (error_code.SDK_UNKNOWN_SERVER_ERROR, error_msg.get_msg('SDK_UNKNOWN_SERVER_ERROR'))
        except ValueError:
            # failed to parse body as json format
            return (error_code.SDK_UNKNOWN_SERVER_ERROR, error_msg.get_msg('SDK_UNKNOWN_SERVER_ERROR'))

    def do_action_with_exception(self, acs_request):

        # set server response format as json, because thie function will
        # parse the response so which format doesn't matter
        acs_request.set_accept_format('json')

        status, headers, body = self._implementation_of_do_action(acs_request)

        request_id = None
        ret = body

        try:
            body_obj = json.loads(str(body))
            request_id = body_obj.get('RequestId')
            ret = body_obj
        except ValueError:
            # in case the response body is not a json string, return the raw data instead
            pass

        if status != 200:
            server_error_code, server_error_message = self._parse_error_info_from_response_body(body)
            raise ServerException(server_error_code, server_error_message, http_status=status, request_id=request_id)

        return body

    def do_action(self, acs_request):
        warnings.warn("do_action() method is deprecated, please use do_action_with_exception() instead.", DeprecationWarning)
        status, headers, body = self._implementation_of_do_action(acs_request)
        return body

    def get_response(self, acs_request):
        warnings.warn("get_response() method is deprecated, please use do_action_with_exception() instead.", DeprecationWarning)
        return self._implementation_of_do_action(acs_request)


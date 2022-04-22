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

#coding=utf-8

import os
import sys
import json
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from ..request import RpcRequest
from ..http_service.http_response import HttpResponse
from ..acs_exception import exceptions as exs
from ..acs_exception import error_code, error_msg

LOCATION_SERVICE_PRODUCT_NAME="Location"
LOCATION_SERVICE_DOMAIN="location.aliyuncs.com"
LOCATION_SERVICE_VERSION="2015-06-12"
LOCATION_SERVICE_DESCRIBE_ENDPOINT_ACTION="DescribeEndpoint"
LOCATION_SERVICE_REGION="cn-hangzhou"

class DescribeEndpointRequest(RpcRequest):

    def __init__(self, product_name, version, action_name, region_id, service_code):
        RpcRequest.__init__(self, product_name, version, action_name, 'hhh')

        self.add_query_param("Id", region_id)
        self.add_query_param("ServiceCode", service_code)
        self.set_accept_format("JSON")


class LocationService:

    def __init__(self, client):
        self.__clinetRef = client
        self.__cache = {}
        self.__service_product_name = LOCATION_SERVICE_PRODUCT_NAME
        self.__service_domain = LOCATION_SERVICE_DOMAIN
        self.__service_version = LOCATION_SERVICE_VERSION
        self.__service_region = LOCATION_SERVICE_REGION
        self.__service_action = LOCATION_SERVICE_DESCRIBE_ENDPOINT_ACTION

    def set_location_service_attr(self, region=None, product_name=None, domain=None,version=None):
        if region is not None:
            self.__service_region = region

        if product_name is not None:
            self.__service_product_name = product_name

        if domain is not None:
            self.__service_domain = domain

        if version is not None:
            self.__service_version = version

    def find_product_domain(self, region_id, service_code):
        key = "%s_&_%s" %(region_id, service_code)
        domain = self.__cache.get(key)
        if domain is None:
            domain = self.find_product_domain_from_location_service(region_id, service_code)
            if domain is not None:
                self.__cache[key] = domain

        return domain


    def find_product_domain_from_location_service(self, region_id, service_code):

        request = DescribeEndpointRequest(self.__service_product_name,
                                           self.__service_version,
                                           self.__service_action,
                                           region_id,
                                           service_code)
        try:
            content = request.get_content()
            method = request.get_method()
            header = request.get_signed_header(self.__service_region, self.__clinetRef.get_access_key(),
                                                   self.__clinetRef.get_access_secret())
            if self.__clinetRef.get_user_agent() is not None:
                header['User-Agent'] = self.__clinetRef.get_user_agent()
                header['x-sdk-client'] = 'python/2.0.0'
            protocol = request.get_protocol_type()
            url = request.get_url(self.__service_region, self.__clinetRef.get_access_key(),
                                  self.__clinetRef.get_access_secret())
            response = HttpResponse(self.__service_domain, url, method, {} if header is None else header, protocol, content,
                                    self.__clinetRef.get_port())

            status, header, body = response.get_response_object()
            result = json.loads(body)
            if status == 200:
                return result.get('Endpoint')
            elif status >= 400 and status < 500:
                # print "serviceCode=" + service_code + " get location error! code=" + result.get('Code') +", message =" + result.get('Message')
                return None
            elif status >= 500:
                raise exs.ServerException(result.get('Code'), result.get('Message'))
            else:
                raise exs.ClientException(result.get('Code'), result.get('Message'))
        except IOError:
            raise exs.ClientException(error_code.SDK_SERVER_UNREACHABLE, error_msg.get_msg('SDK_SERVER_UNREACHABLE'))
        except AttributeError:
            raise exs.ClientException(error_code.SDK_INVALID_REQUEST, error_msg.get_msg('SDK_INVALID_REQUEST'))

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

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from .http_service import protocol_type as PT
from .http_service import method_type as MT
from .http_service import format_type as FT
from .auth import rpc_signature_composer as rpc_signer
from .auth import roa_signature_composer as roa_signer
from .auth import oss_signature_composer as oss_signer
from .auth import md5_tool
import abc
import base64

"""
Acs request model.

Created on 9/19/2017

@author: guangyao
"""

STYLE_RPC = 'RPC'
STYLE_ROA = 'ROA'
STYLE_OSS = 'OSS'


class AcsRequest:
    """
    Acs request base class. This class wraps up common parameters for a request.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, product, version=None,
                 action_name=None,
                 location_service_code=None,
                 accept_format=None,
                 protocol_type=PT.HTTP,
                 method=None):
        """

        :param product:
        :param version:
        :param action_name:
        :param params:
        :param resource_owner_account:
        :param protocol_type:
        :param accept_format:
        :return:
        """
        self.__version = version
        self.__product = product
        self.__action_name = action_name
        self.__protocol_type = protocol_type
        self.__accept_format = accept_format
        self.__params = {}
        self.__method = method
        self.__header = {}
        self.__uri_pattern = None
        self.__uri_params = None
        self.__content = None
        self.__location_service_code = location_service_code

    def add_query_param(self, k, v):
        if self.__params is None:
            self.__params = {}
        self.__params[k] = v

    def get_uri_pattern(self):
        return self.__uri_pattern

    def get_uri_params(self):
        return self.__uri_params

    def get_product(self):
        return self.__product

    def get_version(self):
        return self.__version

    def get_action_name(self):
        return self.__action_name

    def get_accept_format(self):
        return self.__accept_format

    def get_protocol_type(self):
        return self.__protocol_type

    def get_query_params(self):
        return self.__params

    def get_method(self):
        return self.__method

    def set_uri_pattern(self, pattern):
        self.__uri_pattern = pattern

    def set_uri_params(self, params):
        self.__uri_params = params

    def set_method(self, method):
        self.__method = method

    def set_product(self, product):
        self.__product = product

    def set_version(self, version):
        self.__version = version

    def set_action_name(self, action_name):
        self.__action_name = action_name

    def set_accept_format(self, accept_format):
        self.__accept_format = accept_format

    def set_protocol_type(self, protocol_type):
        self.__protocol_type = protocol_type

    def set_query_params(self, params):
        self.__params = params

    def set_content(self, content):
        """

        :param content: ByteArray
        :return:
        """
        self.__content = content

    def get_content(self):
        """

        :return: ByteArray
        """
        return self.__content

    def get_headers(self):
        """

        :return: Dict
        """
        return self.__header

    def set_headers(self, headers):
        """

        :param headers: Dict
        :return:
        """
        self.__header = headers

    def add_header(self, k, v):
        if self.__header is None:
            self.__header = dict(k=v)
        else:
            self.__header[k] = v

    def set_user_agent(self, agent):
        self.add_header('User-Agent', agent)

    def set_location_service_code(self, location_service_code):
        self.__location_service_code = location_service_code

    def get_location_service_code(self):
        return self.__location_service_code

    @abc.abstractmethod
    def get_style(self):
        pass

    @abc.abstractmethod
    def get_url(self, region_id, ak, secret):
        pass

    @abc.abstractmethod
    def get_signed_header(self, region_id, ak, secret):
        pass


class RpcRequest(AcsRequest):
    """
    Class to compose an RPC style request with.
    """

    def __init__(self, product, version, action_name, location_service_code=None, format=None, protocol=None):
        AcsRequest.__init__(self, product, version, action_name, location_service_code, format, protocol, MT.GET)
        self.__style = STYLE_RPC

    def get_style(self):
        return self.__style

    def __get_sign_params(self):
        req_params = self.get_query_params()
        if req_params is None:
            req_params = {}
        req_params['Version'] = self.get_version()
        req_params['Action'] = self.get_action_name()
        req_params['Format'] = self.get_accept_format()
        return req_params

    def get_url(self, region_id, ak, secret):
        sign_params = self.__get_sign_params()
        if 'RegionId' not in sign_params.keys():
            sign_params['RegionId'] = region_id
        url = rpc_signer.get_signed_url(sign_params, ak, secret, self.get_accept_format(), self.get_method())
        return url

    def get_signed_header(self, region_id=None, ak=None, secret=None):
        return {}


class RoaRequest(AcsRequest):
    """
    Class to compose an ROA style request with.
    """

    def __init__(self, product, version, action_name, location_service_code=None, method=None, headers=None, uri_pattern=None, path_params=None,
                 protocol=None):
        """

        :param product: String, mandatory
        :param version: String, mandatory
        :param action_name: String, mandatory
        :param method: String
        :param headers: Dict
        :param uri_pattern: String
        :param path_params: Dict
        :param protocol: String
        :return:
        """
        AcsRequest.__init__(self, product, version, action_name, location_service_code, FT.RAW, protocol, method)
        self.__style = STYLE_ROA
        self.__method = method
        self.__header = headers
        self.__uri_pattern = uri_pattern
        self.__path_params = path_params

    def get_style(self):
        """

        :return: String
        """
        return self.__style

    def get_path_params(self):
        return self.__path_params

    def set_path_params(self, path_params):
        self.__path_params = path_params

    def add_path_param(self, k, v):
        if self.__path_params is None:
            self.__path_params = {}
        self.__path_params[k] = v

    def __get_sign_params(self):
        req_params = self.get_query_params()
        if req_params is None:
            req_params = {}
        req_params['Version'] = self.get_version()
        req_params['Action'] = self.get_action_name()
        req_params['Format'] = self.get_accept_format()
        return req_params

    def get_signed_header(self, region_id, ak, secret):
        """
        Generate signed header
        :param region_id: String
        :param ak: String
        :param secret: String
        :return: Dict
        """
        sign_params = self.get_query_params()
        if (self.get_content() is not None):
            md5_str = md5_tool.get_md5_base64_str(self.get_content())
            self.add_header('Content-MD5', md5_str)
        if 'RegionId' not in sign_params.keys():
            sign_params['RegionId'] = region_id
        signed_headers = roa_signer.get_signature_headers(sign_params, ak, secret,
                                                          self.get_accept_format(),
                                                          self.get_headers(),
                                                          self.get_uri_pattern(),
                                                          self.get_path_params(),
                                                          self.get_method())
        return signed_headers

    def get_url(self, region_id, ak=None, secret=None):
        """
        Compose request url without domain
        :param region_id: String
        :return: String
        """
        sign_params = self.get_query_params()
        if region_id not in sign_params.keys():
            sign_params['RegionId'] = region_id
        url = roa_signer.get_url(self.get_uri_pattern(), sign_params, self.get_path_params())
        return url


class OssRequest(AcsRequest):
    def __init__(self, product, version, action_name, location_service_code, bucket=None, method=None,
                 headers=None, uri_pattern=None, path_params=None, protocol=None):
        """

        :param product: String, mandatory
        :param version: String, mandatory
        :param action_name: String, mandatory
        :param bucket: String
        :param method: String
        :param headers: Dict
        :param uri_pattern: String
        :param path_params: Dict
        :param protocol: String
        :return:
        """
        AcsRequest.__init__(self, product, version, action_name, location_service_code, FT.XML, protocol, method)
        self.__style = STYLE_OSS
        self.__bucket = bucket
        self.__method = method
        self.__header = headers
        self.__uri_pattern = uri_pattern
        self.__path_params = path_params

    def get_style(self):
        return self.__style

    def get_path_params(self):
        """

        :return: dict
        """
        return self.__path_params

    def set_path_params(self, path_params):
        self.__path_params = path_params

    def add_path_param(self, k, v):
        if self.__path_params is None:
            self.__path_params = {}
        self.__path_params[k] = v

    def __get_sign_params(self):
        req_params = self.get_query_params()
        if req_params is None:
            req_params = {}
        req_params['Version'] = self.get_version()
        req_params['Action'] = self.get_action_name()
        req_params['Format'] = self.get_accept_format()
        return req_params

    def get_signed_header(self, region_id, ak, secret, ):
        """
        Compose signed headers.
        :param region_id: String
        :param ak: String
        :param secret: String
        :return:
        """
        sign_params = self.get_query_params()
        if 'RegionId' not in sign_params.keys():
            sign_params['RegionId'] = region_id
        signed_headers = oss_signer.get_signature_headers(sign_params, ak, secret, self.get_accept_format(),
                                                          self.get_headers(),
                                                          self.get_uri_pattern(), self.get_path_params(),
                                                          self.get_method(), self.__bucket)
        return signed_headers

    def get_url(self, region_id, ak=None, secret=None):
        """
        Generate request url without domain
        :param region_id: String
        :return: String
        """
        sign_params = self.get_query_params()
        if 'RegionId' not in sign_params.keys():
            sign_params['RegionId'] = region_id
        url = oss_signer.get_url(sign_params, self.get_uri_pattern(), self.get_path_params())
        return url

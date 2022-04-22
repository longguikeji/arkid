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
 # Unless required by applicable law or agreed to in writing,
 # software distributed under the License is distributed on an
 # "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 # KIND, either express or implied.  See the License for the
 # specific language governing permissions and limitations
 # under the License.

 #coding=utf-8

__author__ = 'guangyao'
import os
import sys

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from . import roa_signature_composer
from . import sha_hmac1 as mac1
from ..utils import parameter_helper as helper
from urllib import parse

ACCEPT = "Accept"
CONTENT_MD5 = "Content-MD5"
CONTENT_TYPE = "Content-Type"
DATE = "Date"
QUERY_SEPARATOR = "&"
HEADER_SEPARATOR = "\n"

def __init__():
    pass

def refresh_sign_parameters(parameters, access_key_id, format="JSON", signer=mac1):
    parameters["Date"] = helper.get_rfc_2616_date()
    return parameters

def __build_query_string(uri, queries):
    sorted_map = sorted(queries.items(), key=lambda queries:queries[0])
    if len(sorted_map) > 0:
        uri += "?"
        for (k,v) in sorted_map:
            uri += k
            if v is not None:
                uri += "="
                uri += v
            uri += roa_signature_composer.QUERY_SEPARATOR
    if uri.find(roa_signature_composer.QUERY_SEPARATOR) >= 0:
        uri = uri[0:(len(uri)-1)]
    return uri

def compose_string_to_sign(method, queries, uri_pattern=None, headers=None, paths=None, signer=mac1):
    sign_to_string = ""
    sign_to_string += method
    sign_to_string += HEADER_SEPARATOR
    if headers.has_key(CONTENT_MD5) and headers[CONTENT_MD5] is not None:
        sign_to_string += headers[CONTENT_MD5]
    sign_to_string += HEADER_SEPARATOR
    if headers.has_key(CONTENT_TYPE) and headers[CONTENT_TYPE] is not None:
        sign_to_string += headers[CONTENT_TYPE]
    sign_to_string += HEADER_SEPARATOR
    if headers.has_key(DATE) and headers[DATE] is not None:
        sign_to_string += headers[DATE]
    sign_to_string += HEADER_SEPARATOR
    sign_to_string += roa_signature_composer.build_canonical_headers(headers, "x-oss-")
    sign_to_string += __build_query_string(uri_pattern, queries)
    return sign_to_string

def get_signature(queries, access_key, secret, format, headers, uri_pattern, paths, method, signer=mac1, bucket_name=None):
    headers = refresh_sign_parameters(parameters=headers, access_key_id=access_key,format=format)
    uri = uri_pattern
    if bucket_name is not None:
        uri = "/"+bucket_name+uri
    sign_to_string = compose_string_to_sign(method=method, queries=queries, headers=headers, uri_pattern=uri, paths=paths)
    signature = signer.get_sign_string(sign_to_string, secret=secret)
    return signature

def get_signature_headers(queries, access_key, secret, format, headers, uri_pattern, paths, method, bucket_name, signer=mac1):
    signature = get_signature(queries, access_key, secret, format, headers, uri_pattern, paths, method, signer, bucket_name)
    headers["Authorization"] = "OSS "+access_key+":"+signature
    return headers

def get_url(queries, uri_pattern, path_parameters):
    url = ""
    url += roa_signature_composer.replace_occupied_parameters(uri_pattern, path_parameters)
    if not url.endswith("?"):
        url += "?"
    url += parse.urlencode(queries)
    if url.endswith("?"):
        url = url[0:(len(url)-1)]
    return url
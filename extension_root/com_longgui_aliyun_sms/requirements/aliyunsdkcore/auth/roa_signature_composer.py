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
sys.path.insert(0, parentdir)
from . import sha_hmac1 as mac1
from ..utils import parameter_helper as helper
from ..http_service import format_type as FormatType
from urllib import parse

ACCEPT = "Accept"
CONTENT_MD5 = "Content-MD5"
CONTENT_TYPE = "Content-Type"
DATE = "Date"
QUERY_SEPARATOR = "&"
HEADER_SEPARATOR = "\n"

def __init__():
    pass

# this function will append the necessary parameters for signer process.
# parameters: the orignal parameters
# signer: sha_hmac1 or sha_hmac256
# accessKeyId: this is aliyun_access_key_id
# format: XML or JSON
# input parameters is headers
def refresh_sign_parameters(parameters, access_key_id, format, signer=mac1):
    if parameters is None or not isinstance(parameters, dict):
        parameters = dict()
    if format is None:
        format = FormatType.RAW
    parameters["Date"] = helper.get_rfc_2616_date()
    parameters["Accept"] = FormatType.map_format_to_accept(format)
    parameters["x-acs-signature-method"] = signer.get_signer_name()
    parameters["x-acs-signature-version"] = signer.get_singer_version()
    return parameters


def compose_string_to_sign(method, queries, uri_pattern=None, headers=None, paths=None, signer=mac1):
    sign_to_string = ""
    sign_to_string += method
    sign_to_string += HEADER_SEPARATOR
    if headers.has_key(ACCEPT) and headers[ACCEPT] is not None:
        sign_to_string += headers[ACCEPT]
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
    uri = replace_occupied_parameters(uri_pattern, paths)
    sign_to_string += build_canonical_headers(headers, "x-acs-")
    sign_to_string += __build_query_string(uri, queries)
    return sign_to_string

def replace_occupied_parameters(uri_pattern, paths):
    result = uri_pattern
    if paths is not None:
        for (key, value) in paths.items():
            target = "[" + key + "]"
            result = result.replace(target, value)
    return result

# change the give headerBegin to the lower() which in the headers
# and change it to key.lower():value
def build_canonical_headers(headers, header_begin):
    result = ""
    unsort_map = dict()
    for (key, value) in headers.iteritems():
        if key.lower().find(header_begin) >= 0:
            unsort_map[key.lower()] = value
    sort_map = sorted(unsort_map.items(), key=lambda d: d[0])
    for (key, value) in sort_map:
        result += key + ":" +value
        result += HEADER_SEPARATOR
    return result

def split_sub_resource(uri):
    return uri.split("?")

def __build_query_string(uri, queries):
    uri_parts = split_sub_resource(uri)
    if len(uri_parts) >1 and uri_parts[1] is not None:
        queries[uri_parts[1]] = None
    query_builder = uri_parts[0]
    sorted_map = sorted(queries.items(), key=lambda queries:queries[0])
    if len(sorted_map) > 0:
        query_builder += "?"
    for (k,v) in sorted_map:
        query_builder += k
        if v is not None:
            query_builder += "="
            query_builder += str(v)
        query_builder += QUERY_SEPARATOR
    if query_builder.endswith(QUERY_SEPARATOR):
        query_builder = query_builder[0:(len(query_builder)-1)]
    return query_builder

def get_signature(queries, access_key, secret, format, headers, uri_pattern, paths, method, signer=mac1):
    headers = refresh_sign_parameters(parameters=headers, access_key_id=access_key,format=format)
    sign_to_string = compose_string_to_sign(method=method, queries=queries, headers=headers, uri_pattern=uri_pattern, paths=paths)
    signature = signer.get_sign_string(sign_to_string, secret=secret)
    return signature

def get_signature_headers(queries, access_key, secret, format, headers, uri_pattern, paths, method, signer=mac1):
    signature = get_signature(queries, access_key, secret, format, headers, uri_pattern, paths, method, signer)
    headers["Authorization"] = "acs "+access_key+":"+signature
    return headers

def get_url(uri_pattern, queries, path_parameters):
    url = ""
    url += replace_occupied_parameters(uri_pattern, path_parameters)
    if not url.endswith("?"):
        url += "?"
    url += parse.urlencode(queries)
    if url.endswith("?"):
        url = url[0:(len(url)-1)]
    return url

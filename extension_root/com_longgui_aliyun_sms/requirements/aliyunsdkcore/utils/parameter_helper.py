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

import hashlib
import base64
import uuid
import time
from urllib import parse
import sys

TIME_ZONE = "GMT"
FORMAT_ISO_8601 = "%Y-%m-%dT%H:%M:%SZ"
FORMAT_RFC_2616 = "%a, %d %b %Y %X GMT"

def get_uuid():
    return str(uuid.uuid4())

def get_iso_8061_date():
    return time.strftime(FORMAT_ISO_8601, time.gmtime())

def get_rfc_2616_date():
    return time.strftime(FORMAT_RFC_2616, time.gmtime())

def md5_sum(content):
    return base64.standard_b64encode(hashlib.md5(content).digest())

def percent_encode(encodeStr):
    encodeStr = str(encodeStr)
    if sys.stdin.encoding is None:
        res = parse.quote(encodeStr.decode('cp936').encode('utf8'), '')
    else:
        res = parse.quote(encodeStr.decode(sys.stdin.encoding).encode('utf8'), '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res

if __name__ == "__main__":
    print(get_uuid())
    print(get_iso_8061_date())
    print(get_rfc_2616_date())

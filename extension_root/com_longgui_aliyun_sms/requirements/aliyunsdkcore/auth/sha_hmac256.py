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

import hmac
import hashlib
import base64

class ShaHmac256:
    def __init__(self):
        pass

    def get_sign_string(self, source, accessSecret):
        h = hmac.new(accessSecret, source, hashlib.sha256)
        signature = base64.encodestring(h.digest()).strip()
        return signature

    def get_signer_name(self):
        return "HMAC-SHA256"

    def get_singer_version(self):
        return "1.0"

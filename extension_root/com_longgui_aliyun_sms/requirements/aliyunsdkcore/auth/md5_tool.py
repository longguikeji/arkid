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

"""
MD5 tools module.

Created on 9/19/2017

@author: guangyao
"""

import hashlib
import base64



def _get_md5(content):
    m = hashlib.md5()
    m.update(memoryview(content))
    return m.digest()

def get_md5_base64_str(content):
    return base64.encodestring(_get_md5(content)).strip()

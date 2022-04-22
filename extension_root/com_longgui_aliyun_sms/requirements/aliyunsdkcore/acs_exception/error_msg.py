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

"""
Acs error message module.

Created on 9/19/2017

@author: guangyao
"""

__dict = dict(SDK_INVALID_REGION_ID='Can not find endpoint to access.',
              SDK_SERVER_UNREACHABLE='Unable to connect server',
              SDK_INVALID_REQUEST='The request is not a valid AcsRequest.',
              SDK_MISSING_ENDPOINTS_FILER='Internal endpoints info is missing.',
              SDK_UNKNOWN_SERVER_ERROR="Can not parse error message from server response.")


def get_msg(code):
	return __dict.get(code)

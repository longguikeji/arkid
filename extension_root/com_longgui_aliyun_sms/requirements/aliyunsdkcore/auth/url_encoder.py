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
from urllib import parse
import sys

"""
Acs url encoder module.

Created on 9/19/2017

@author: guangyao
"""


def get_encode_str(params):
	"""
	transforms parameters to encoded string
	:param params: dict parameters
	:return: string
	"""
	list_params = sorted(params.iteritems(), key=lambda d: d[0])
	encode_str = parse.urlencode(list_params)
	if sys.stdin.encoding is None:
		res = parse.quote(encode_str.decode('cp936').encode('utf8'), '')
	else:
		res = parse.quote(encode_str.decode(sys.stdin.encoding).encode('utf8'), '')
	res = res.replace("+","%20")
	res = res.replace("*","%2A")
	res = res.replace("%7E","~")
	return res
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

from aliyunsdkcore.request import RpcRequest

class SendBatchSmsRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Dysmsapi', '2017-05-25', 'SendBatchSms')

	def get_TemplateCode(self):
		return self.get_query_params().get('TemplateCode')

	def set_TemplateCode(self,TemplateCode):
		self.add_query_param('TemplateCode',TemplateCode)

	def get_templateParamJson(self):
		return self.get_query_params().get('templateParamJson')

	def set_templateParamJson(self,templateParamJson):
		self.add_query_param('templateParamJson',templateParamJson)

	def get_ResourceOwnerAccount(self):
		return self.get_query_params().get('ResourceOwnerAccount')

	def set_ResourceOwnerAccount(self,ResourceOwnerAccount):
		self.add_query_param('ResourceOwnerAccount',ResourceOwnerAccount)

	def get_SmsUpExtendCodeJson(self):
		return self.get_query_params().get('SmsUpExtendCodeJson')

	def set_SmsUpExtendCodeJson(self,SmsUpExtendCodeJson):
		self.add_query_param('SmsUpExtendCodeJson',SmsUpExtendCodeJson)

	def get_ResourceOwnerId(self):
		return self.get_query_params().get('ResourceOwnerId')

	def set_ResourceOwnerId(self,ResourceOwnerId):
		self.add_query_param('ResourceOwnerId',ResourceOwnerId)

	def get_SignNameJson(self):
		return self.get_query_params().get('SignNameJson')

	def set_SignNameJson(self,SignNameJson):
		self.add_query_param('SignNameJson',SignNameJson)

	def get_OwnerId(self):
		return self.get_query_params().get('OwnerId')

	def set_OwnerId(self,OwnerId):
		self.add_query_param('OwnerId',OwnerId)

	def get_PhoneNumberJson(self):
		return self.get_query_params().get('PhoneNumberJson')

	def set_PhoneNumberJson(self,PhoneNumberJson):
		self.add_query_param('PhoneNumberJson',PhoneNumberJson)

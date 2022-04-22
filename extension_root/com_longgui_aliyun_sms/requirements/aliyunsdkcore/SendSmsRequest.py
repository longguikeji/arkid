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

from .request import RpcRequest
class SendSmsRequest(RpcRequest):

	def __init__(self):
		RpcRequest.__init__(self, 'Dysmsapi', '2017-05-25', 'SendSms')

	def get_OutId(self):
		return self.get_query_params().get('OutId')

	def set_OutId(self,OutId):
		self.add_query_param('OutId',OutId)

	def get_SignName(self):
		return self.get_query_params().get('SignName')

	def set_SignName(self,SignName):
		self.add_query_param('SignName',SignName)

	def get_ResourceOwnerId(self):
		return self.get_query_params().get('ResourceOwnerId')

	def set_ResourceOwnerId(self,ResourceOwnerId):
		self.add_query_param('ResourceOwnerId',ResourceOwnerId)

	def get_OwnerId(self):
		return self.get_query_params().get('OwnerId')

	def set_OwnerId(self,OwnerId):
		self.add_query_param('OwnerId',OwnerId)

	def get_TemplateCode(self):
		return self.get_query_params().get('TemplateCode')

	def set_TemplateCode(self,TemplateCode):
		self.add_query_param('TemplateCode',TemplateCode)

	def get_PhoneNumbers(self):
		return self.get_query_params().get('PhoneNumbers')

	def set_PhoneNumbers(self,PhoneNumbers):
		self.add_query_param('PhoneNumbers',PhoneNumbers)

	def get_ResourceOwnerAccount(self):
		return self.get_query_params().get('ResourceOwnerAccount')

	def set_ResourceOwnerAccount(self,ResourceOwnerAccount):
		self.add_query_param('ResourceOwnerAccount',ResourceOwnerAccount)

	def get_TemplateParam(self):
		return self.get_query_params().get('TemplateParam')

	def set_TemplateParam(self,TemplateParam):
		self.add_query_param('TemplateParam',TemplateParam)
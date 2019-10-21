# -*- coding: utf-8 -*-

import uuid
import json
import logging
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from aliyunsdkcore.acs_exception.exceptions import ServerException
from .request.v20170525.SendSmsRequest import SendSmsRequest


from .constants import (
    SMS_ALIYUN_REGION,
    SMS_ALIYUN_PRODUCT_NAME,
    SMS_ALIYUN_DOMAIN,
)


class SMSAliyunManager(object):

    def __init__(self, access_key, access_key_secret):
        self.access_key = access_key
        self.access_key_secret = access_key_secret

    def send_auth_code(self, mobile, vc_code, sign_name, template_code):
        template_param = {"code": str(vc_code)}

        self.send_sms(mobile, sign_name, template_code, template_param)

    def send_sms(self, mobile, sign_name, template_code, template_param=None):
        business_id = uuid.uuid1()
        smsRequest = SendSmsRequest()
        smsRequest.set_TemplateCode(template_code)

        if template_param is not None:
            smsRequest.set_TemplateParam(template_param)

        smsRequest.set_OutId(business_id)
        smsRequest.set_SignName(sign_name)
        smsRequest.set_PhoneNumbers(mobile)
        acs_client = AcsClient(self.access_key, self.access_key_secret, SMS_ALIYUN_REGION)
        region_provider.add_endpoint(SMS_ALIYUN_PRODUCT_NAME, SMS_ALIYUN_REGION, SMS_ALIYUN_DOMAIN)

        try:
            smsResponse = acs_client.do_action_with_exception(smsRequest)
            logging.error(smsResponse)
            data = json.loads(str(smsResponse, 'utf-8'))
            if data['Code'] == 'OK':
                return True
            else:
                logging.error('SMS[{}]: '.format(mobile) + data['Message'])
                raise RuntimeError
        except ServerException as exc:
            raise exc


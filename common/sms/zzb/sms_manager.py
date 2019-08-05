# coding: utf-8

import requests
import xmltodict
import logging

from settings import (
    SMS_ZZB_USERID,
    SMS_ZZB_ACCOUNT,
    SMS_ZZB_PASSWORD,
    SMS_AUTH_CODE_TEMPLATE,
)


SMS_ZZB_URL = 'http://10086.dxcx.com/sms.aspx'

class SMSZzbManager(object):

    action_send = 'send'

    def __init__(self):
        pass

    def send_auth_code(self, mobile, vc_code, expired_minutes, template_id):
        content = SMS_AUTH_CODE_TEMPLATE.format(vc_code)
        self.send_sms(mobile, content)

    def send_sms(self, mobile, content):
        number_count = len(mobile.split(','))
        params = {
            'userid': SMS_ZZB_USERID,
            'account': SMS_ZZB_ACCOUNT,
            'password': SMS_ZZB_PASSWORD,
            'mobile': mobile,
            'content': content,
            'action': self.action_send,
            'countnumber': number_count,
            'mobilenumber': number_count,
        }

        r = requests.post(SMS_ZZB_URL, params)

        try:
            return_data = xmltodict.parse(r.content)
            return_sms = return_data['returnsms']
            if return_sms['returnstatus'] == 'Success':
                return True
            else:
                logging.error(return_sms['message'])
                raise Exception
        except Exception, e:
            raise RuntimeError('runtime error raised')



import time
import uuid
import hashlib
import base64
import requests
import logging

from .constants import API_URL
from common.provider import SMSProvider
from typing import Dict, List


class HuaWeiSMSProvider(SMSProvider):

    def __init__(self, access_key: str, secret_key: str, template: str, signature: str, sender: str) -> None:
        self.access_key = access_key
        self.secret_key = secret_key
        self.template = template
        self.signature = signature
        self.sender = sender

    def send_auth_code(self, mobile: str, code: str):
        '''
        发送短信
        @param mobile: string 电话号码 示例:8615123456789
        @param code: string 验证码
        '''
        template_param = [str(code)]
        self.send_sms([mobile], self.template, template_param)

    def build_wsse_header(self):
        '''
        构造X-WSSE参数值
        '''
        now = time.strftime('%Y-%m-%dT%H:%M:%SZ')  # Created
        nonce = str(uuid.uuid4()).replace('-', '')  # Nonce
        digest = hashlib.sha256((nonce + now + self.secret_key).encode()).hexdigest()

        digestBase64 = base64.b64encode(digest.encode()).decode()  # PasswordDigest
        return 'UsernameToken Username="{}",PasswordDigest="{}",Nonce="{}",Created="{}"'.format(self.access_key, digestBase64, nonce, now)

    def send_sms(self, mobiles: List[str], template_code: str, template_param: Dict[str, str], status_callback: str = '') -> bool:
        '''
        发送短信
        @param mobiles: arr 示例:['+8615123456789']多个号码之间用英文逗号分隔
        @param template_code: string 模板id
        @param template_param: arr 模板参数
        @param status_callback: string 选填,短信状态报告接收地址,推荐使用域名,为空或者不填表示不接收状态报告
        '''
        # 请求Headers
        header = {
            'Authorization': 'WSSE realm="SDP",profile="UsernameToken",type="Appkey"',
            'X-WSSE': self.build_wsse_header()
        }
        # 手机号处理
        mobile = ''
        for index, item in enumerate(mobiles):
            if '+' not in item:
                mobile = mobile.join('+86{}'.format(str(item)))
            else:
                mobile = mobile.join(str(item))
            if index != len(mobiles) - 1:
                mobile = mobile.join(',')
        # 请求Body
        form_data = {
            'from': self.sender,
            'to': mobile,
            'templateId': template_code,
            'templateParas': str(template_param),
            'statusCallback': status_callback,
            'signature': self.signature
        }
        logging.error('短信请求体')
        logging.error(form_data)
        result = requests.post(API_URL, data=form_data, headers=header, verify=False)
        result_json = result.json()
        logging.error('短信返回体')
        logging.error(result_json)
        if result_json.get('code') == "000000":
            return True
        else:
            return False

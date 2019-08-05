# coding: utf-8

import string
import random
from vendor.CCPRestSDK import REST  # missing

SERVER_IP = 'app.cloopen.com'
SERVER_PORT = '8883'
SOFT_VERSION = '2013-12-26'

AUTH_CODE_NUM = 'NUM'
AUTH_CODE_LTR = 'LTR'
AUTH_CODE_MIX = 'MIX'


class SMSManager(object):

    def __init__(self, account_sid, account_token, sub_account_sid,
                 sub_account_token, app_id, server_ip=SERVER_IP,
                 server_port=SERVER_PORT, soft_version=SOFT_VERSION):
        """
        初始化

        :param str account_sid:      主账号
        :param str account_token:    主账号口令
        :param str sub_account_sid:  子帐号
        :param str sub_account_token:子帐号口令
        :param str app_id:           应用ID
        :param str server_ip:        请求地址
        :param str server_port:      请求端口
        :param str soft_version:     REST版本号
        """

        self.manager = REST(server_ip, server_port, soft_version, True)
        self.manager.setAccount(account_sid, account_token)
        self.manager.setSubAccount(sub_account_sid, sub_account_token)
        self.manager.setAppId(app_id)

    def send_auth_code(self, mobile, code,
                       expired_minutes=2, template_id=1):
        """
        发送短信验证码

        :param str mobile:          必选参数 接收号码
        :param str code:     必选参数 验证码内容
        :param int expired_minutes: 可选参数 时间限制（min），默认2min
        :param int template_id:     可选参数 模版ID，默认为1
        :returns: 发送成功返回True，否则False
        :rtype: bool
        """

        resp = self.manager.sendTemplateSMS(mobile,
                                            [code, expired_minutes],
                                            template_id)
        return self._check_result(resp)

    def send_sms_msg(self, mobile, datas, expired_minutes=2, template_id=1):
        """
        发送短信验证码

        :param str mobile:          必选参数 接收号码
        :param str datas:     可选参数 短信需要的参数
        :param int expired_minutes: 可选参数 时间限制（min），默认2min
        :param int template_id:     可选参数 模版ID，默认为1
        :returns: 发送成功返回True，否则False
        :rtype: bool
        """

        datas.append(expired_minutes)
        resp = self.manager.sendTemplateSMS(mobile, datas, template_id)
        return self._check_result(resp)

    def send_voice_code(self, mobile, code, display_num='',
                        resp_url='', lang='', user_data='', play_times=3):
        """
        发送语音验证码

        :param str mobile:      必选参数 接收号码
        :param str code:        必选参数 验证码内容，限制长度4-8位
        :param str display_num: 可选参数 显示的主叫号码
        :param str resp_url:    可选参数 语音验证码状态通知回调地址，云通讯平台向该Url地址发送呼叫结果通知
        :param str lang:        可选参数 语言类型
        :param str user_data:   可选参数 第三方私有数据
        :param int play_times:  可选参数 播放次数，1-3次，默认3次
        :returns: 发送成功返回True，否则False
        :rtype: bool
        """

        if len(code) > 8 or len(code) < 4:
            raise Exception('验证码长度不符合规范，限制长度4-8位')
        resp = self.manager.voiceVerify(code, play_times, mobile,
                                        display_num, resp_url, lang, user_data)
        return self._check_result(resp)

    def gen_auth_code(self, digits=4, pattern=AUTH_CODE_NUM):
        """
        生成验证码

        :param int digits:  可选参数 验证码长度,默认4位
        :param int pattern: 可选参数 验证码样式，默认为'NUM'代表纯数字，'LTR'代表纯字母，'MIX'代表字母数字混合
        :returns: 根据长度与样式生成的验证码
        :rtype: str
        """

        if pattern == AUTH_CODE_MIX:
            code = ''
            for index in xrange(digits):
                if index == 0:
                    code = code + random.choice(string.uppercase)
                elif index == 1:
                    code = code + random.choice(string.digits)
                else:
                    code = code + random.choice(string.uppercase+string.digits)
            return code
        elif pattern == AUTH_CODE_LTR:
            return ''.join(
                [(random.choice(string.uppercase)) for _ in xrange(digits)])
        else:
            return ''.join(
                [(random.choice(string.digits)) for _ in xrange(digits)])

    def _check_result(self, resp):
        """
        检查是否发送成功

        :param dict resp:必选参数 回应结果
        :returns: 发送成功返回True，否则False
        :rtype: bool
        """

        try:
            ret = resp['statusCode'] == '000000'
        except KeyError:
            ret = False
        finally:
            return ret

'''
serializers for SMS
'''
import random
import string    # pylint:disable=deprecated-module
import time

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings

from oneid_meta.models import User, Invitation, SMSConfig
from oneid.utils import redis_conn
from common.sms.aliyun.sms_manager import SMSAliyunManager
from infrastructure.views.captcha_img import check_captcha    # pylint: disable=unused-import
from infrastructure.utils.sms import is_mobile, is_cn_mobile


def send_sms(mobile, code, template):
    '''
    向指定手机发送验证
    '''
    sms_config = SMSConfig.get_current()
    smser = SMSAliyunManager(
        access_key=sms_config.access_key,
        access_key_secret=sms_config.access_secret,
    )
    signature = sms_config.signature if is_cn_mobile(mobile) else sms_config.signature_i18n
    mobile = ''.join([literal for literal in mobile if literal.isdigit()])

    # `+86 18812341234` -> `8618812341234`
    try:
        smser.send_auth_code(
            mobile=mobile,
            vc_code=code,
            sign_name=signature,
            template_code=template,
        )
    except RuntimeError as exc:
        if 'MOBILE_NUMBER_ILLEGAL' in repr(exc):
            raise ValidationError({'mobile': 'invalid'})
        raise exc


def gen_code():
    '''
    gen random code
    '''
    return ''.join(random.choice(string.digits) for _ in range(6))


class SMSClaimSerializer(serializers.Serializer):
    '''
    Serializer for SMS Claim
    - 对于已登录用户，发送短信无需验证码
    '''
    captcha = serializers.CharField(required=False)
    captcha_key = serializers.CharField(required=False)
    mobile = serializers.CharField()

    username = serializers.CharField(required=False)

    def get_template_id(self):    # pylint: disable=no-self-use
        '''
        读取模板id
        '''
        sms_config = SMSConfig.get_current()
        i18n = not is_cn_mobile(self.validated_data['mobile'])    # 国内号码即使加上区号，也无法使用国际模板
        return sms_config.get_template_code("code", i18n)

    def validate_mobile(self, value):    # pylint: disable=no-self-use
        '''
        校验手机
        '''
        if is_mobile(value):
            return value

        raise ValidationError('invalid')

    def validate(self, attrs):
        '''
        validate data
        '''
        validated_data = super().validate(attrs)

        request = self.context.get("request")
        if request.user.is_authenticated:
            return validated_data

        # close captcha validator
        # if 'captcha' not in attrs:
        #     raise ValidationError({'captcha': ['This field is required.']})
        # if 'captcha_key' not in attrs:
        #     raise ValidationError({'captcha_key': ['This field is required.']})

        # if not check_captcha(captcha_code=attrs['captcha'], captcha_key=attrs['captcha_key']):
        #     raise ValidationError({'captcha': ['invalid']})

        return validated_data

    def create(self, validated_data):
        '''
        send sms
        '''
        code = gen_code()
        mobile = validated_data['mobile']
        send_sms(mobile, code, self.get_template_id())
        key = self.gen_sms_code_key(mobile)
        value = code

        redis_conn.set(key, value, ex=settings.SMS_LIFESPAN.seconds)
        return '_'

    @staticmethod
    def gen_sms_code_key(mobile):
        '''
        生成短信验证码的key
        '''
        return f'sms:{mobile}'

    @staticmethod
    def gen_sms_token_key(sms_token):
        '''
        生成sms_token的key
        '''
        return f'sms_token:{sms_token}'

    def update(self, instance, validated_data):
        pass

    @classmethod
    def check_sms(cls, data):
        '''
        check sms code with mobile and code
        '''
        mobile = data.get('mobile', None)
        if not mobile:
            raise ValidationError({'mobile': ['This field is required.']})

        code = data.get('code', None)
        if not code:
            raise ValidationError({'code': ['This field is required.']})

        res = redis_conn.get(cls.gen_sms_code_key(mobile))
        if res:
            send_code = res
            if send_code and code == send_code:
                sms_token = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(24))
                redis_conn.set(cls.gen_sms_token_key(sms_token), mobile, ex=settings.SMS_LIFESPAN.seconds * 10)
                redis_conn.delete(cls.gen_sms_code_key(mobile))
                return sms_token, int(time.time()) + settings.SMS_LIFESPAN.seconds * 10
        raise ValidationError({'code': ['invalid']})

    @classmethod
    def check_sms_token(cls, sms_token):
        '''
        通过短信验证后，拿到的身份凭证。用于临时性的二次验证。
        有效期长于之前的验证码，一般短于账号密码登录后的token。
        '''
        key = cls.gen_sms_token_key(sms_token)
        res = redis_conn.get(key)
        if res:
            return {'mobile': res}    # mobile
        raise ValidationError({'sms_token': ['invalid']})

    @classmethod
    def clear_sms_token(cls, sms_token):
        '''
        清除sms_token
        '''
        redis_conn.delete(cls.gen_sms_token_key(sms_token))


class ResetPWDSMSClaimSerializer(SMSClaimSerializer):
    '''
    重置密码发送短信时，需要该手机号、账号已存在且匹配
    '''

    username = serializers.CharField(required=True)

    def get_template_id(self):
        '''
        读取模板ID
        '''
        sms_config = SMSConfig.get_current()
        i18n = not is_cn_mobile(self.validated_data['mobile'])
        return sms_config.get_template_code("reset_pwd", i18n) or \
            sms_config.get_template_code("code", i18n)

    @staticmethod
    def gen_sms_code_key(mobile):
        '''
        生成短信验证码的key
        '''
        return f'sms:reset_password:{mobile}'

    @staticmethod
    def gen_sms_token_key(sms_token):
        '''
        生成sms_token的key
        '''
        return f'sms_token:reset_password:{sms_token}'

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        mobile = validated_data['mobile']
        username = validated_data['username']
        if not User.valid_objects.filter(mobile=mobile, username=username).exists():
            raise ValidationError({'mobile': ['invalid']})

        return validated_data


class RegisterSMSClaimSerializer(SMSClaimSerializer):
    '''
    用户注册时发短信，需要该手机号不存在
    '''
    def get_template_id(self):
        '''
        读取模板ID
        '''
        sms_config = SMSConfig.get_current()
        i18n = not is_cn_mobile(self.validated_data['mobile'])
        return sms_config.get_template_code("register", i18n) or \
            sms_config.get_template_code("code", i18n)

    @staticmethod
    def gen_sms_code_key(mobile):
        '''
        生成短信验证码的key
        '''
        return f'sms:register:{mobile}'

    @staticmethod
    def gen_sms_token_key(sms_token):
        '''
        生成sms_token的key
        '''
        return f'sms_token:register:{sms_token}'

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        mobile = validated_data['mobile']
        if User.valid_objects.filter(mobile=mobile).exists():
            raise ValidationError({'mobile': 'existed'})
        return validated_data


class LoginSMSClaimSerializer(SMSClaimSerializer):
    '''
    用户登录时发短信，需要该手机号存在
    '''
    def get_template_id(self):
        '''
        读取模板ID
        '''
        sms_config = SMSConfig.get_current()
        i18n = not is_cn_mobile(self.validated_data['mobile'])
        return sms_config.get_template_code("login", i18n) or \
            sms_config.get_template_code("code", i18n)

    @staticmethod
    def gen_sms_code_key(mobile):
        '''
        生成短信验证码的key
        '''
        return f'sms:login:{mobile}'

    @staticmethod
    def gen_sms_token_key(sms_token):
        '''
        生成sms_token的key
        '''
        return f'sms_token:login:{sms_token}'

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        mobile = validated_data['mobile']
        if not User.valid_objects.filter(mobile=mobile).exists():
            raise ValidationError({'mobile': 'invalid'})
        return validated_data


class UserActivateSMSClaimSerializer(SMSClaimSerializer):
    '''
    激活用户时发短信，需要该用户处于激活状态
    '''

    key = serializers.CharField(required=True)
    mobile = serializers.CharField(required=False)

    def get_template_id(self):
        '''
        读取模板ID
        '''
        sms_config = SMSConfig.get_current()
        i18n = not is_cn_mobile(self.validated_data['mobile'])
        return sms_config.get_template_code("activate", i18n) or \
            sms_config.get_template_code("code", i18n)

    @staticmethod
    def gen_sms_code_key(mobile):
        '''
        生成短信验证码的key
        '''
        return f'sms:activate:{mobile}'

    @staticmethod
    def gen_sms_token_key(sms_token):
        '''
        生成sms_token的key
        '''
        return f'sms_token:activate:{sms_token}'

    def validate(self, attrs):
        key = attrs.get('key', '')
        if not key:
            raise ValidationError({'key': ['this field is required']})

        invitation = Invitation.parse(key)
        if invitation is None:
            raise ValidationError({'key': ['invalid']})

        if invitation.is_expired:
            raise ValidationError({'key': ['expired']})

        if not invitation.invitee.mobile:
            raise ValidationError({'key': ['invalid']})

        return {
            'key': key,
            'mobile': invitation.invitee.mobile,
        }


class UpdateMobileSMSClaimSerializer(SMSClaimSerializer):
    '''
    用户自助修改手机号
    '''

    mobile = serializers.CharField(required=True)
    password = serializers.CharField(required=False)

    def get_template_id(self):
        '''
        读取模板ID
        '''
        sms_config = SMSConfig.get_current()
        i18n = not is_cn_mobile(self.validated_data['mobile'])
        return sms_config.get_template_code("reset_mobile", i18n) or \
            sms_config.get_template_code("code", i18n)

    @staticmethod
    def gen_sms_code_key(mobile):
        '''
        生成短信验证码的key
        '''
        return 'sms:update_mobile:{mobile}'

    @staticmethod
    def gen_sms_token_key(sms_token):
        '''
        生成sms_token的key
        '''
        return f'sms_token:update_mobile:{sms_token}'

    def validate_mobile(self, value):
        '''
        校验手机号是否被占用
        '''
        value = super().validate_mobile(value)
        user = self.context['request'].user
        if User.valid_objects.filter(mobile=value).exclude(id=user.id).exists():
            raise ValidationError('existed')
        return value

    def validate_password(self, value):
        '''
        校验密码是否正确
        '''
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError('invalid')
        return value

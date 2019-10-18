'''
serializers for email
'''
import uuid as uuid_utils

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
from django.template.loader import render_to_string

from tasksapp.tasks import send_email
from oneid_meta.models import User, Invitation, CompanyConfig
from oneid.utils import redis_conn


class EmailClaimSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    Serializer for email Claim
    '''

    email = serializers.CharField()

    @staticmethod
    def gen_email_token():
        '''
        生成email_token
        '''
        return uuid_utils.uuid4().hex

    @staticmethod
    def validate_email(value):
        '''
        校验邮箱格式合法性
        '''
        return value

    def create(self, validated_data):
        '''
        send sms
        '''
        send_email.delay(validated_data.get('email'), **self.gen_email())
        return '_'

    def gen_email(self, *args, **kwargs):    # pylint: disable=unused-argument, no-self-use
        '''
        定制邮件内容
        '''
        raise NotImplementedError

    def check_email_token(self, email_token):
        '''
        校验email_token
        '''
        raise NotImplementedError

    @staticmethod
    def gen_email_token_key(email_token):
        '''
        生成email_token的key
        '''
        raise NotImplementedError

    @classmethod
    def clear_email_token(cls, email_token):
        '''
        清除email_token
        '''
        redis_conn.delete(cls.gen_email_token_key(email_token))

    def update(self, instance, validated_data):
        '''
        override
        '''


class RegisterEmailClaimSerializer(EmailClaimSerializer):
    '''
    发送注册验证邮件
    '''
    @staticmethod
    def gen_email_token_key(email_token):
        '''
        生成email_token的key
        '''
        return f'email:register:{email_token}'

    def validate_email(self, value):
        '''
        需邮件未被使用
        '''
        private_email = super().validate_email(value)

        if User.valid_objects.filter(private_email=private_email).exists():
            raise ValidationError({'email': ['existed']})

        return private_email

    def gen_email(self, *args, **kwargs):
        '''
        生成注册验证邮件
        '''
        subject = '[ArkID] 欢迎注册使用ArkID'

        email_token = self.gen_email_token()
        link = settings.BASE_URL + settings.FE_EMAIL_REGISTER_URL + f'?email_token={email_token}'
        key = self.gen_email_token_key(email_token)
        redis_conn.set(key, self.validated_data['email'], ex=60 * 60 * 24 * 3)

        content = f'点击以下链接完成验证，3天之内有效：</br><a href="{link}">{link}</a>'
        html = render_to_string('email/common.html', {
            'company': CompanyConfig.get_current().name_cn,
            'content': content
        })

        return {
            'subject': subject,
            'content': html,
        }

    @classmethod
    def check_email_token(cls, email_token):
        '''
        校验email_token
        '''
        key = cls.gen_email_token_key(email_token)
        res = redis_conn.get(key)
        if res:
            return {'email': res}
        raise ValidationError({'email_token': ['invalid']})


class ResetPWDEmailClaimSerializer(EmailClaimSerializer):
    '''
    发送重置密码验证邮件
    '''
    @staticmethod
    def gen_email_token_key(email_token):
        '''
        生成email_token的key
        '''
        return f'email:reset_password:{email_token}'

    def validate_email(self, value):
        '''
        需邮件已被使用
        '''
        private_email = super().validate_email(value)

        if not User.valid_objects.filter(private_email=private_email).exists():
            raise ValidationError({'email': ['invalid']})
        return private_email

    def gen_email(self, *args, **kwargs):
        '''
        生成重置密码邮件
        '''
        subject = '[ArkID] 您正在重置ArkID登录密码'
        email_token = self.gen_email_token()
        link = settings.BASE_URL + settings.FE_EMAIL_RESET_PWD_URL + f'?email_token={email_token}'
        key = self.gen_email_token_key(email_token)
        redis_conn.set(key, self.validated_data['email'], ex=60 * 60 * 24 * 3)

        content = f'点击以下链接完成验证，3天之内有效：</br><a href="{link}">{link}</a>'
        html = render_to_string('email/common.html', {
            'company': CompanyConfig.get_current().name_cn,
            'content': content
        })

        return {
            'subject': subject,
            'content': html,
        }

    @classmethod
    def check_email_token(cls, email_token):
        '''
        校验email_token
        '''
        key = cls.gen_email_token_key(email_token)
        res = redis_conn.get(key)
        if res:
            email = res
            user = User.valid_objects.filter(private_email=email).first()
            if user:
                return {'email': email, 'name': user.name, 'username': user.username}
        raise ValidationError({'email_token': ['invalid']})


class UserActivateEmailClaimSerializer(EmailClaimSerializer):
    '''
    发送用户激活验证邮件
    '''

    email = serializers.CharField(required=False)
    key = serializers.CharField(required=True)

    @staticmethod
    def gen_email_token_key(email_token):
        '''
        生成email_token的key
        '''
        return f'email:activate_user:{email_token}'

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        key = validated_data['key']

        invitation = Invitation.parse(key)
        if invitation is None:
            raise ValidationError({'key': ['invalid']})

        if invitation.is_expired:
            raise ValidationError({'key': ['expired']})

        if not invitation.invitee.private_email:
            raise ValidationError({'key': ['invalid']})

        return {
            'email': invitation.invitee.private_email,
            'key': key,
        }

    def gen_email(self, *args, **kwargs):
        subject = '[ArkID] 您正在激活ArkID账号'
        email_token = self.gen_email_token()
        link = settings.BASE_URL + settings.FE_EMAIL_ACTIVATE_USER_URL + f'?email_token={email_token}'
        key = self.gen_email_token_key(email_token)

        redis_conn.hset(key, 'email', self.validated_data['email'])
        redis_conn.hset(key, 'key', self.validated_data['key'])
        redis_conn.expire(key, 60 * 60 * 24 * 3)

        content = f'点击以下链接完成验证，3天之内有效：</br><a href="{link}">{link}</a>'
        html = render_to_string('email/common.html', {
            'company': CompanyConfig.get_current().name_cn,
            'content': content
        })

        return {
            'subject': subject,
            'content': html,
        }

    @classmethod
    def check_email_token(cls, email_token):
        '''
        校验email_token
        '''
        key = cls.gen_email_token_key(email_token)
        res = redis_conn.hgetall(key)
        if res:
            email = res[b'email'].decode()
            invite_key = res[b'key'].decode()
            user = User.valid_objects.filter(private_email=email).first()
            if user:
                return {'email': email, 'name': user.name, 'username': user.username, 'key': invite_key}
        raise ValidationError({'email_token': ['invalid']})


class UpdateEmailEmailClaimSerializer(EmailClaimSerializer):
    '''
    发送修改邮箱验证邮件
    '''

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    @staticmethod
    def gen_email_token_key(email_token):
        '''
        生成email_token的key
        '''
        return f'email:update_email:{email_token}'

    def gen_email(self, *args, **kwargs):
        '''
        生成修改私人邮箱邮件
        '''
        subject = '[ArkID]您正在重置ArkID私人邮箱'
        email_token = self.gen_email_token()
        link = settings.BASE_URL + settings.FE_EMAIL_UPDATE_EMAIL_URL + f'?email_token={email_token}'
        key = self.gen_email_token_key(email_token)

        redis_conn.hset(key, 'email', self.validated_data['email'])
        redis_conn.hset(key, 'username', self.context['request'].user.username)
        redis_conn.expire(key, 60 * 60 * 24 * 3)

        content = f'点击以下链接完成验证，3天之内有效：</br><a href="{link}">{link}</a>'
        html = render_to_string('email/common.html', {
            'company': CompanyConfig.get_current().name_cn,
            'content': content
        })

        return {
            'subject': subject,
            'content': html,
        }

    def validate_email(self, value):
        '''
        新邮箱需未被使用
        '''
        user = self.context['request'].user
        value = super().validate_email(value)
        if User.valid_objects.filter(private_email=value).exclude(id=user.id).exists():
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

    @classmethod
    def check_email_token(cls, email_token):
        '''
        校验email_token
        '''
        key = cls.gen_email_token_key(email_token)
        res = redis_conn.hgetall(key)
        if res:
            email = res[b'email'].decode()
            username = res[b'username'].decode()
            user = User.valid_objects.filter(username=username).first()
            if user:
                return {'email': email, 'username': username, 'name': user.name}
        raise ValidationError({'email_token': ['invalid']})

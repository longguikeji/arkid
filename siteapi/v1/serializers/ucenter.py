'''
serializers for ucenter
'''
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from common.django.drf.serializer import DynamicFieldsModelSerializer
from oneid_meta.models import User, Invitation
from executer.core import CLI
from infrastructure.serializers.sms import (
    SMSClaimSerializer,
    RegisterSMSClaimSerializer,
    ResetPWDSMSClaimSerializer,
    UserActivateSMSClaimSerializer,
    UpdateMobileSMSClaimSerializer,
)
from infrastructure.serializers.email import (
    RegisterEmailClaimSerializer,
    ResetPWDEmailClaimSerializer,
    UserActivateEmailClaimSerializer,
    UpdateEmailEmailClaimSerializer,
)

from oneid.auth_backend import OneIDBasicAuthBackend
from siteapi.v1.serializers.utils import username_valid


class SetPasswordSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    reset password
    - by sms
    - by email
    - by old_password
    '''

    email = serializers.CharField(required=False)
    email_token = serializers.CharField(required=False)

    mobile = serializers.CharField(required=False)
    sms_token = serializers.CharField(required=False, write_only=True)

    username = serializers.CharField(required=False)
    old_password = serializers.CharField(required=False, write_only=True)

    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        request = self.context.get("request")

        # 短信重置密码
        mobile = validated_data.get('mobile')
        if mobile:
            user = User.valid_objects.filter(mobile=validated_data.get('mobile')).first()
            if not user:
                raise ValidationError({'mobile': ['invalid']})

            sms_token = validated_data.get('sms_token', '')
            if sms_token:
                mobile = ResetPWDSMSClaimSerializer.check_sms_token(sms_token)['mobile']
                ResetPWDSMSClaimSerializer.clear_sms_token(sms_token)
                if mobile != user.mobile:
                    raise ValidationError({'mobile': ['invalid']})
                validated_data['user'] = user
                return validated_data

        # 邮件重置密码
        email = validated_data.get('email')
        if email:
            user = User.valid_objects.filter(private_email=email).first()
            if not user:
                raise ValidationError({'user': 'invalid'})
            email_token = validated_data.get('email_token', '')
            if email_token:
                email = ResetPWDEmailClaimSerializer.check_email_token(email_token)['email']
                ResetPWDEmailClaimSerializer.clear_email_token(email_token)
                if email != user.private_email:
                    raise ValidationError({'email': ['invalid']})
                validated_data['user'] = user
                return validated_data

        # 旧密码重置密码
        username = validated_data.get('username')
        if username:
            user = User.valid_objects.filter(username=username).first()
            if not user:
                raise ValidationError({'user': 'invalid'})
            old_password = validated_data.get('old_password', '')
            if old_password:
                res = OneIDBasicAuthBackend().authenticate(request, user.username, old_password)
                if res is None:
                    raise ValidationError({'old_password': ['invalid']})
                validated_data['user'] = user
                return validated_data

        raise ValidationError({'auth': ['Invalid']})

    def update(self, instance, validated_data):
        user = validated_data['user']
        password = validated_data.get('new_password')
        CLI(user=user).set_user_password(user, password)
        user.revoke_token()
        user.require_reset_password = False
        user.save(update_fields=['require_reset_password'])
        return user

    @staticmethod
    def validate_new_password(value):
        """密码复杂度检验"""
        validate_password(value)
        return value


class UserRegisterSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer user register
    '''

    username = serializers.CharField(max_length=16, min_length=4, required=True)
    password = serializers.CharField()
    sms_token = serializers.CharField(required=False)
    email_token = serializers.CharField(required=False)

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'username',
            'password',
            'sms_token',
            'email_token',
        )

    def validate(self, attrs):
        '''
        校验token，验重
        '''
        validated_data = super().validate(attrs)
        if not (validated_data.get('sms_token', '') or validated_data.get('email_token', '')):
            raise ValidationError({'auth_token': ['auth_token is required, like "sms_token" or "email_token"']})

        username = validated_data['username']
        if User.valid_objects.filter(username=username).exists():
            raise ValidationError({'username': ['existed']})

        if not username_valid(username):
            raise ValidationError({'username': ['invalid']})

        sms_token = validated_data.get('sms_token', '')
        if sms_token:
            mobile = RegisterSMSClaimSerializer.check_sms_token(sms_token)['mobile']
            RegisterSMSClaimSerializer.clear_sms_token(sms_token)
            if User.valid_objects.filter(mobile=mobile).exists():
                raise ValidationError({'mobile': ['existed']})
            validated_data['mobile'] = mobile

        email_token = validated_data.get('email_token', '')
        if email_token:
            private_email = RegisterEmailClaimSerializer.check_email_token(email_token)['email']
            RegisterEmailClaimSerializer.clear_email_token(email_token)
            if User.valid_objects.filter(private_email=private_email).exists():
                raise ValidationError({'private_email': ['existed']})
            validated_data['private_email'] = private_email

        return validated_data

    def create(self, validated_data):
        '''
        创建用户
        '''
        cli = CLI()
        password = validated_data.pop('password')
        user = cli.create_user(validated_data)
        user.from_register = True
        user.save()
        cli.set_user_password(user, password)
        return user

    @staticmethod
    def validate_password(value):
        """密码复杂度检验"""
        validate_password(value)
        return value


class UserAlterMobileSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    serializer for alter user mobile
    '''

    old_mobile_sms_token = serializers.CharField(required=True, write_only=True)
    new_mobile_sms_token = serializers.CharField(required=True, write_only=True)

    new_mobile = serializers.CharField(required=False, source='mobile')

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        old_mobile = SMSClaimSerializer.check_sms_token(validated_data.get('old_mobile_sms_token'))['mobile']
        new_mobile = UpdateMobileSMSClaimSerializer.check_sms_token(
            validated_data.get('new_mobile_sms_token'))['mobile']    # pylint: disable=line-too-long

        request = self.context.get("request")
        user = request.user

        if user.mobile != old_mobile:
            raise ValidationError({'old_mobile': 'invalid mobile'})

        if User.valid_objects.filter(mobile=new_mobile).exists():
            raise ValidationError({'new_mobile': 'has been used'})

        validated_data.update(new_mobile=new_mobile)

        return validated_data

    def update(self, instance, validated_data):
        instance.mobile = validated_data.pop('new_mobile')
        instance.save()
        return instance


class UserInvitedProfileSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    serialzier for user to set profile after accept invitation
    '''

    password = serializers.CharField(required=True, write_only=True)
    username = serializers.CharField(required=False)
    key = serializers.CharField(required=True)

    sms_token = serializers.CharField(required=False)
    email_token = serializers.CharField(required=False)

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        key = validated_data.pop('key')
        invitation = Invitation.parse(key)
        if not invitation:
            raise ValidationError({'key': ['invalid']})

        user = invitation.invitee
        user_validated = False

        username = validated_data.get('username', '')
        if username and User.valid_objects.filter(username=username).exclude(pk=user.pk).exists():
            raise ValidationError({'username': ['existed']})

        sms_token = validated_data.pop('sms_token', '')
        if sms_token:
            mobile = UserActivateSMSClaimSerializer.check_sms_token(sms_token)['mobile']
            UserActivateSMSClaimSerializer.clear_sms_token(sms_token)
            if mobile != user.mobile:
                raise ValidationError({'sms_token': ['invalid']})
            user_validated = True

        email_token = validated_data.pop('email_token', '')
        if email_token:
            email = UserActivateEmailClaimSerializer.check_email_token(email_token)['email']
            UserActivateEmailClaimSerializer.clear_email_token(email_token)
            if email != user.private_email:
                raise ValidationError({'email_token': ['invalid']})
            user_validated = True

        if not user_validated:
            raise ValidationError({'auth_token': ['must provide "email_token" or "sms_token"']})

        validated_data.update(user=user)
        return validated_data


class UserContactSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    用户联系方式
    '''

    email_token = serializers.CharField(required=False)
    sms_token = serializers.CharField(required=False)

    def validate(self, attrs):
        user = self.context['request'].user
        validated_data = super().validate(attrs)

        sms_token = validated_data.pop('sms_token', '')
        if sms_token:
            mobile = UpdateMobileSMSClaimSerializer.check_sms_token(sms_token)['mobile']
            UpdateMobileSMSClaimSerializer.clear_sms_token(sms_token)
            if User.valid_objects.filter(mobile=mobile).exclude(id=user.id).exists():
                raise ValidationError({'mobile': ['existed']})
            validated_data['mobile'] = mobile

        email_token = validated_data.pop('email_token', '')
        if email_token:
            res = UpdateEmailEmailClaimSerializer.check_email_token(email_token)
            UpdateEmailEmailClaimSerializer.clear_email_token(email_token)
            email = res['email']
            username = res['username']

            if user.username != username:
                raise ValidationError({'email_token': ['invalid']})

            if User.valid_objects.filter(private_email=email).exclude(id=user.id).exists():
                raise ValidationError({'email': ['existed']})

            validated_data['private_email'] = email

        return validated_data

    def update(self, instance, validated_data):
        '''
        更新手机号、私人邮箱
        '''
        cli = CLI()
        cli.update_user(instance, validated_data)
        return instance


class BindSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    - by sms_token
    - by user_id
    '''

    sms_token = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)

    class Meta:
        '''
        关联User表
        '''
        model = User
        fields = (
            'sms_token',
            'user_id',
        )

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        mobile = SMSClaimSerializer.check_sms_token(validated_data['sms_token'])['mobile']
        SMSClaimSerializer.clear_sms_token(validated_data['sms_token'])
        user = User.valid_objects.filter(mobile=mobile).first()
        validated_data['user'] = user
        return validated_data

    def update(self, instance, validated_data):
        cli = CLI()
        cli.update_user(instance, validated_data)
        return instance


class RegisterAndBindSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer user register
    '''
    username = serializers.CharField(required=True, min_length=4, max_length=16)
    password = serializers.CharField(required=True)
    sms_token = serializers.CharField(required=True)
    user_id = serializers.CharField(required=True)

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'username',
            'password',
            'sms_token',
            'user_id',
        )

    def validate(self, attrs):
        '''
        校验token，验重
        '''
        validated_data = super().validate(attrs)
        if not validated_data.get('sms_token', ''):
            raise ValidationError({'auth_token': ['auth_token is required, like "sms_token"']})

        username = validated_data['username']
        if User.valid_objects.filter(username=username).exists():
            raise ValidationError({'username': ['existed']})

        if not username_valid(username):
            raise ValidationError({'username': ['invalid']})

        sms_token = validated_data.get('sms_token', None)
        if sms_token:
            mobile = SMSClaimSerializer.check_sms_token(sms_token)['mobile']
            SMSClaimSerializer.clear_sms_token(sms_token)
            validated_data['mobile'] = mobile
        return validated_data

    def create(self, validated_data):
        '''
        创建用户
        '''
        cli = CLI()
        password = validated_data.pop('password')
        user = cli.create_user(validated_data)
        user.from_register = True
        user.save()
        cli.set_user_password(user, password)
        return user

'''
serializers for ucenter wechat
'''
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from oneid_meta.models import User, WechatUser
from common.django.drf.serializer import DynamicFieldsModelSerializer
from infrastructure.serializers.sms import SMSClaimSerializer
from executer.core import CLI


class WechatRegisterAndBindSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer wechat user register
    '''
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    sms_token = serializers.CharField(required=True)
    # wechat_user_id = serializers.CharField(required=False)
    user_id = serializers.CharField(required=True)

    class Meta:
        '''
        关联企业微信用户表
        '''
        model = WechatUser

        fields = (
            'username', 'password', 'sms_token', 'user_id'
        # 'wechat_user_id',
        )

    def validate(self, attrs):
        '''
        校验token, 验重
        '''
        validated_data = super().validate(attrs)
        if not validated_data.get('sms_token', ''):
            raise ValidationError({'auth_token': ['auth_tokne is required, like "sms_token']})

        username = validated_data['username']
        if User.valid_objects.filter(username=username).exists():
            raise ValidationError({'username': ['existed']})

        sms_token = validated_data.get('sms_token', None)
        if sms_token:
            mobile = SMSClaimSerializer.check_sms_token(sms_token)['mobile']
            SMSClaimSerializer.clear_sms_token(sms_token)
            validated_data['mobile'] = mobile
        validated_data['unionid'] = validated_data['user_id']

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


class WechatBindSerializer(serializers.Serializer):    # pylint: disable=abstract-method
    '''
    wechat bind
    - by sms_token
    - by uinonid
    '''

    sms_token = serializers.CharField(required=True)
    # wechat_user_id = serializers.CharField(required=False)
    user_id = serializers.CharField(required=True)

    class Meta:
        '''
        关联wechatUser表
        '''
        model = WechatUser
        fields = (
            'sms_token', 'user_id'
        # 'wechat_user_id',
        )

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        validated_data['unionid'] = validated_data['user_id']
        mobile = SMSClaimSerializer.check_sms_token(validated_data['sms_token'])['mobile']
        SMSClaimSerializer.clear_sms_token(validated_data['sms_token'])
        user = User.valid_objects.filter(mobile=mobile).first()
        validated_data['user'] = user
        return validated_data

    def update(self, instance, validated_data):
        cli = CLI()
        cli.update_user(instance, validated_data)
        return instance

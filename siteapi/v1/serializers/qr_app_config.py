'''
外部网站信息返回校验
'''
from rest_framework import serializers

from common.django.drf.serializer import DynamicFieldsModelSerializer

from oneid_meta.models import AlipayConfig, DingConfig

from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.error_utils import APICallError
from thirdparty_data_sdk.dingding.dingsdk import constants


class PublicDingConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for DingConfig
    '''
    class Meta:    # pylint: disable=missing-docstring

        model = DingConfig

        fields = (
            'app_key',
        # 'app_secret',
            'corp_id',
        # 'corp_secret',
            'qr_app_id',
        # 'qr_app_secret',
        )


class PublicAlipayConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for AlipayConfig
    '''
    class Meta:    # pylint: disable=missing-docstring

        model = AlipayConfig

        fields = ('app_id', )


class DingConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for DingConfig
    '''
    app_secret = serializers.CharField(write_only=True)
    corp_secret = serializers.CharField(write_only=True)
    qr_app_secret = serializers.CharField(write_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = DingConfig

        fields = (
            'app_key',
            'app_secret',
            'corp_id',
            'corp_secret',
            'app_valid',
            'corp_valid',
            'qr_app_id',
            'qr_app_secret',
            'qr_app_valid',
        )

        read_only_fields = (
            'app_valid',
            'corp_valid',
        )

    def update(self, instance, validated_data):
        '''
        - update data
        - validated updated data
        '''
        instance.__dict__.update(validated_data)
        instance.app_valid = self.validate_app_config(instance)
        instance.corp_valid = self.validate_corp_config(instance)
        instance.qr_app_valid = self.validate_qr_app_config(instance)
        update_fields = ['app_valid', 'corp_valid', 'qr_app_valid']
        update_fields += ['app_key', 'app_secret'] if instance.app_valid else []
        update_fields += ['corp_id', 'corp_secret'] if instance.corp_valid else []
        update_fields += ['qr_app_id', 'qr_app_secret'] if instance.qr_app_valid else []
        instance.save(update_fields=update_fields)
        instance.refresh_from_db()
        return instance

    @staticmethod
    def validate_app_config(instance):
        '''
        validate app_key, app_secret
        :rtype: bool
        '''
        try:
            AccessTokenManager(
                app_key=instance.app_key,
                app_secret=instance.app_secret,
                token_version=constants.TOKEN_FROM_APPKEY_APPSECRET,
            ).get_access_token()
            return True
        except APICallError:
            return False

    @staticmethod
    def validate_corp_config(instance):
        '''
        validate corp_id, corp_secret
        :rtype: bool
        '''
        try:
            AccessTokenManager(
                app_key=instance.corp_id,
                app_secret=instance.corp_secret,
                token_version=constants.TOKEN_FROM_CORPID_CORPSECRET,
            ).get_access_token()
            return True
        except APICallError:
            return False

    @staticmethod
    def validate_qr_app_config(instance):
        '''
        validate qr_app_id, qr_app_secret
        :rtype:bool
        '''
        try:
            AccessTokenManager(app_key=instance.qr_app_id,
                               app_secret=instance.qr_app_secret,
                               token_version=constants.TOKEN_FROM_APPID_QR_APP_SECRET).get_access_token()
            return True
        except APICallError:
            return False


class AlipayConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for AlipayConfig
    '''
    app_private_key = serializers.CharField(write_only=True)
    alipay_public_key = serializers.CharField(write_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = AlipayConfig

        fields = (
            'app_id',
            'app_private_key',
            'alipay_public_key',
            'qr_app_valid',
        )

        read_only_fields = ('qr_app_valid', )

    def update(self, instance, validated_data):
        '''
        - update data
        - validated updated data
        '''
        instance.__dict__.update(validated_data)
        instance.qr_app_valid = self.validate_qr_app_config(instance)
        update_fields = ['qr_app_valid']
        update_fields += ['app_id', 'app_private_key', 'alipay_public_key'] if instance.qr_app_valid else []
        instance.save(update_fields=update_fields)
        instance.refresh_from_db()
        return instance

    @staticmethod
    def validate_qr_app_config(instance):
        '''
        validate app_private_key ,alipay_publice_key
        '''
        is_valid = instance.check_valid()
        return is_valid

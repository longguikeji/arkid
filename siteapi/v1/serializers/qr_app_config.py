'''
外部网站信息返回校验
'''

from rest_framework import serializers

from common.django.drf.serializer import DynamicFieldsModelSerializer

from oneid_meta.models import AlipayConfig
from thirdparty_data_sdk.alipay_api.alipay_res_manager import AlipayResManager


class PublicAlipayConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for AlipayConfig
    '''
    class Meta:    # pylint: disable=missing-docstring

        model = AlipayConfig

        fields = ('app_id', )


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
        try:
            AlipayResManager(instance.app_id, instance.app_private_key,\
                instance.alipay_public_key).get_alipay_id_res()
            return True
        except Exception:    # pylint: disable=broad-except
            return False

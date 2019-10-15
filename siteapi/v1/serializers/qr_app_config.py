'''
外部网站信息返回校验
'''

from rest_framework import serializers

from common.django.drf.serializer import DynamicFieldsModelSerializer

from oneid_meta.models import AlipayConfig

class PublicAlipayConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for AlipayConfig
    '''
    class Meta:    # pylint: disable=missing-docstring

        model = AlipayConfig

        fields = (
            'app_id',
        # 'qr_app_secret',
            'qr_callback_url',
        )

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
            'qr_app_valid'
        )

    def update(self, instance, validated_data):
        '''
        - update data
        - validated updated data
        '''
        instance.__dict__.update(validated_data)
        update_fields = ['app_valid', 'app_private_key', 'alipay_public_key']
        instance.save(update_fields=update_fields)
        instance.refresh_from_db()
        return instance

from rest_framework import serializers

class AliyunConfigResponseSerializer(serializers.Serializer):

    access_key = serializers.CharField(required=True,label='Access Key')
    access_secret = serializers.CharField(required=True,label='Access Secret')
    sms_template = serializers.CharField(required=True,label='短信模板')
    sms_signing = serializers.CharField(required=True,label='短信落款')
    international_sms_template = serializers.CharField(label='国际短信模板')
    international_sms_signing = serializers.CharField(label='国际短信落款')


class AliyunSendSMSSerializer(serializers.Serializer):
    
    mobile = serializers.CharField(required=True,label='电话号码')
    
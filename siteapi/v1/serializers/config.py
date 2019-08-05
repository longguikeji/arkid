'''
serializer for config
'''

from django.contrib.sites.models import Site
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from oneid_meta.models import (
    CompanyConfig,
    DingConfig,
    User,
    CustomField,
    NativeField,
    AccountConfig,
    SMSConfig,
    EmailConfig,
)
from common.django.drf.serializer import DynamicFieldsModelSerializer, WritableSerializerMethodField
from thirdparty_data_sdk.dingding.dingsdk.accesstoken_manager import AccessTokenManager
from thirdparty_data_sdk.dingding.dingsdk.error_utils import APICallError
from thirdparty_data_sdk.dingding.dingsdk import constants
from infrastructure.serializers.sms import SMSClaimSerializer


class CompanyConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for CompanyConfig
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = CompanyConfig

        fields = (
            'name_cn',
            'fullname_cn',
            'name_en',
            'fullname_en',
            'icon',
            'address',
            'domain',
            'color',
        )


class AccountConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for AccountConfig
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = AccountConfig

        fields = (
            'allow_register',
            'allow_mobile',
            'allow_email',
        )


class SMSConfigSerializer(DynamicFieldsModelSerializer):
    is_valid = serializers.BooleanField(read_only=True)
    access_secret = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(source='access_secret'),
        required=False,
    )

    class Meta:    # pylint: disable=missing-docstring
        model = SMSConfig

        fields = (
            'vendor',
            'access_key',
            'access_secret',
            'signature',
            'template_code',
            'template_register',
            'template_reset_pwd',
            'template_activate',
            'template_reset_mobile',
            'is_valid',
        )

    def get_access_secret(self, instance):
        return instance.access_secret_encrypt

    def set_access_secret(self, value):
        '''
        pass
        '''


class EmailConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for Email
    '''

    is_valid = serializers.BooleanField(read_only=True)
    access_secret = WritableSerializerMethodField(
        deserializer_field=serializers.CharField(),
        required=False,
    )

    class Meta:    # pylint: disable=missing-docstring

        model = EmailConfig

        fields = (
            'host',
            'port',
            'access_key',
            'access_secret',
            'nickname',
            'is_valid',
        )

    def get_access_secret(self, obj):
        return obj.access_secret_encrypt

    def set_access_secret(self, value):
        pass


class PublicAccountConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for AccountConfig
    public to anyone
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = AccountConfig

        fields = (
            'support_email',
            'support_mobile',
            'support_email_register',
            'support_mobile_register',
        )


class DingConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for DingConfig
    '''
    class Meta:    # pylint: disable=missing-docstring

        model = DingConfig

        fields = (
            'app_key',
            'app_secret',
            'corp_id',
            'corp_secret',
            'app_valid',
            'corp_valid',
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
        super().update(instance, validated_data)
        instance.refresh_from_db()
        instance.app_valid = self.validate_app_config(instance)
        instance.corp_valid = self.validate_corp_config(instance)
        instance.save()
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


class ConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for configs
    '''

    company_config = CompanyConfigSerializer(many=False, required=False)
    ding_config = DingConfigSerializer(many=False, required=False)
    account_config = AccountConfigSerializer(many=False, required=False)
    sms_config = SMSConfigSerializer(many=False, required=False)
    email_config = EmailConfigSerializer(many=False, required=False)

    class Meta:    # pylint: disable=missing-docstring

        model = Site

        fields = (
            'company_config',
            'ding_config',
            'account_config',
            'sms_config',
            'email_config',
        )

    @transaction.atomic()
    def update(self, instance, validated_data):
        company_config_data = validated_data.pop('company_config', None)
        if company_config_data:
            serializer = CompanyConfigSerializer(CompanyConfig.get_current(), company_config_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        ding_config_data = validated_data.pop('ding_config', None)
        if ding_config_data:
            serializer = DingConfigSerializer(DingConfig.get_current(), ding_config_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        account_config_data = validated_data.pop('account_config', None)
        if account_config_data:
            serializer = AccountConfigSerializer(AccountConfig.get_current(), account_config_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        sms_config_data = validated_data.pop('sms_config', None)
        if sms_config_data:
            access_secret = sms_config_data.pop('access_secret', '')
            serializer = SMSConfigSerializer(SMSConfig.get_current(), sms_config_data, partial=True)
            serializer.is_valid(raise_exception=True)    # pylint: disable=not-callable

            config = serializer.save()

            if access_secret and access_secret != config.access_secret_encrypt:
                config.access_secret = access_secret
            config.is_valid = config.check_valid()
            config.save()

        email_config_data = validated_data.pop('email_config', None)
        if email_config_data:
            access_secret = email_config_data.pop('access_secret', '')
            serializer = EmailConfigSerializer(EmailConfig.get_current(), email_config_data, partial=True)
            serializer.is_valid(raise_exception=True)    # pylint: disable=not-callable
            config = serializer.save()
            if access_secret and access_secret != config.access_secret_encrypt:
                config.access_secret = access_secret
            config.is_valid = config.check_valid()
            config.save()

        instance.refresh_from_db()

        return instance


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
        )


class PublicCompanyConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for CompanyConfig
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = CompanyConfig

        fields = (
            'name_cn',
            'fullname_cn',
            'name_en',
            'fullname_en',
            'icon',
            'address',
            'domain',
            'display_name',
            'color',
        )


class MetaConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for meta info
    '''

    company_config = PublicCompanyConfigSerializer(many=False, required=False, read_only=True)
    ding_config = PublicDingConfigSerializer(many=False, required=False, read_only=True)
    account_config = PublicAccountConfigSerializer(many=False, required=False, read_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = Site

        fields = (
            'company_config',
            'ding_config',
            'account_config',
        )


class AlterAdminSerializer(serializers.Serializer):
    '''
    serializer for alter admin
    '''

    old_admin_sms_token = serializers.CharField(required=True, write_only=True)
    new_admin_sms_token = serializers.CharField(required=True, write_only=True)
    new_admin_username = serializers.CharField(required=False, source='username')

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        old_admin_mobile = SMSClaimSerializer.check_sms_token(validated_data.get('old_admin_sms_token'))['mobile']
        new_admin_mobile = SMSClaimSerializer.check_sms_token(validated_data.get('new_admin_sms_token'))['mobile']

        queryset = User.valid_objects.filter(
            mobile=old_admin_mobile,
            is_boss=True,
        )
        if queryset.count() != 1:
            raise ValidationError({"old_admin_sms_token": ["not valid admin"]})
        old_admin = queryset.first()

        queryset = User.valid_objects.filter(mobile=new_admin_mobile, )
        if queryset.count() != 1:
            raise ValidationError({"new_admin_sms_token": ["not valid admin"]})
        new_admin = queryset.first()

        validated_data.update(old_admin=old_admin, new_admin=new_admin)

        return validated_data

    @transaction.atomic()
    def update(self, instance, validated_data):
        old_admin = validated_data.get('old_admin')
        new_admin = validated_data.get('new_admin')

        old_admin.is_boss = False
        old_admin.save()
        old_admin.token_obj.delete()

        new_admin.is_boss = True
        new_admin.save()
        new_admin.token_obj.delete()

        return new_admin

    def create(self, validated_data):
        '''
        skip NotImplementedError
        '''
        return "any"


class CustomFieldSerailizer(DynamicFieldsModelSerializer):
    '''
    serializer for CustomField
    '''
    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = CustomField

        fields = (
            'uuid',
            'name',
            'subject',
            'schema',
            'is_visible',
        )


class NativeFieldSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for NativeField
    '''

    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = NativeField

        fields = (
            'uuid',
            'name',
            'key',
            'subject',
            'schema',
            'is_visible',
            'is_visible_editable',
        )

        read_only_fields = (
            'uuid',
            'name',
            'key',
            'subject',
            'schema',
            'is_visible_editable',
        )

    def update(self, instance, validated_data):
        '''
        update filed
        '''
        if 'is_visible' in validated_data:
            if not instance.is_visible_editable:
                if validated_data['is_visible'] != instance.is_visible:
                    raise ValidationError({'is_visible': [f"this file can't be changed for `{instance.name}`"]})

        return super().update(instance, validated_data)

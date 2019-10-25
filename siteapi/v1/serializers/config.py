'''
serializer for config
'''
from django.contrib.sites.models import Site
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from oneid_meta.models import (CompanyConfig, DingConfig, AlipayConfig, User, Dept, CustomField, NativeField,
                               AccountConfig, SMSConfig, EmailConfig)
from common.django.drf.serializer import DynamicFieldsModelSerializer
from infrastructure.serializers.sms import SMSClaimSerializer
from siteapi.v1.views.utils import gen_uid
from siteapi.v1.serializers.qr_app_config import PublicAlipayConfigSerializer, PublicDingConfigSerializer,\
    AlipayConfigSerializer, DingConfigSerializer
from executer.core import CLI


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
            'allow_ding_qr',
            'allow_alipay_qr',
        )


class SMSConfigSerializer(DynamicFieldsModelSerializer):    # pylint: disable=missing-docstring
    is_valid = serializers.BooleanField(read_only=True)
    access_secret = serializers.CharField(write_only=True, allow_blank=True)

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


class EmailConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for Email
    '''
    is_valid = serializers.BooleanField(read_only=True)
    access_secret = serializers.CharField(
        write_only=True,
        allow_blank=True,
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
            'support_ding_qr',
            'support_alipay_qr',
        )


class ConfigSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for configs
    '''

    company_config = CompanyConfigSerializer(many=False, required=False)
    ding_config = DingConfigSerializer(many=False, required=False)
    account_config = AccountConfigSerializer(many=False, required=False)
    sms_config = SMSConfigSerializer(many=False, required=False)
    email_config = EmailConfigSerializer(many=False, required=False)
    alipay_config = AlipayConfigSerializer(many=False, required=False)

    class Meta:    # pylint: disable=missing-docstring

        model = Site

        fields = ('company_config', 'ding_config', 'account_config', 'sms_config',\
            'email_config', 'alipay_config')

    @transaction.atomic()
    def update(self, instance, validated_data):    # pylint: disable=too-many-locals, too-many-statements, too-many-branches
        company_config_data = validated_data.pop('company_config', None)
        if company_config_data:
            if not Dept.valid_objects.filter(parent__uid='root').exists():
                uid = gen_uid(name=company_config_data.get('name_cn', ''), cls=Dept)
                parent_dept = Dept.valid_objects.filter(uid='root').first()
                cli = CLI()
                dept_data = {
                    'parent_uid': 'root',
                    'name': company_config_data.get('name_cn', ''),
                    'uid': uid,
                }
                child_dept = cli.create_dept(dept_data)
                cli.add_dept_to_dept(child_dept, parent_dept)
            else:
                company_dept = Dept.valid_objects.filter(parent__uid='root').first()
                company_dept.name = company_config_data.get('name_cn', '')
                company_dept.save()
            serializer = CompanyConfigSerializer(CompanyConfig.get_current(), company_config_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        account_config_data = validated_data.pop('account_config', None)
        if account_config_data:
            serializer = AccountConfigSerializer(AccountConfig.get_current(), account_config_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        ding_config_data = validated_data.pop('ding_config', None)
        if ding_config_data:
            serializer = DingConfigSerializer(DingConfig.get_current(), ding_config_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        sms_config_data = validated_data.pop('sms_config', None)
        if sms_config_data:
            access_secret = sms_config_data.pop('access_secret', '')
            config = SMSConfig.get_current()
            serializer = SMSConfigSerializer(config, sms_config_data, partial=True)
            serializer.is_valid(raise_exception=True)    # pylint: disable=not-callable
            config.__dict__.update(serializer.validated_data)

            if access_secret:
                config.access_secret = access_secret
            if not config.check_valid():
                raise ValidationError({'sms': ['invalid']})
            config.is_valid = True
            config.save()

        email_config_data = validated_data.pop('email_config', None)
        if email_config_data:
            access_secret = email_config_data.pop('access_secret', '')
            config = EmailConfig.get_current()
            serializer = EmailConfigSerializer(config, email_config_data, partial=True)
            serializer.is_valid(raise_exception=True)    # pylint: disable=not-callable
            config.__dict__.update(serializer.validated_data)

            if access_secret:
                config.access_secret = access_secret
            if not config.check_valid():
                raise ValidationError({'email': ['invalid']})
            config.is_valid = True
            config.save()

        alipay_config_data = validated_data.pop('alipay_config', None)
        if alipay_config_data:
            serializer = AlipayConfigSerializer(AlipayConfig.get_current(), alipay_config_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        instance.refresh_from_db()

        return instance


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
    alipay_config = PublicAlipayConfigSerializer(many=False, required=False, read_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = Site

        fields = (
            'company_config',
            'ding_config',
            'account_config',
            'alipay_config',
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

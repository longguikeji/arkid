#!/usr/bin/env python3
from rest_framework import serializers
from inventory.models import CustomField, NativeField
from rest_framework.exceptions import ValidationError
from common.serializer import BaseDynamicFieldModelSerializer
from api.v1.fields.custom import create_html_field
from config.models import PrivacyNotice, PasswordComplexity
from tenant.models import Tenant
from django.utils.translation import gettext_lazy as _


class CustomFieldSerailizer(BaseDynamicFieldModelSerializer):
    '''
    serializer for CustomField
    '''

    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:  # pylint: disable=missing-docstring

        model = CustomField

        fields = (
            'uuid',
            'name',
            'subject',
            'schema',
            'is_visible',
        )
        extra_kwargs = {
            'uuid': {'read_only': True},
            'subject': {'read_only': True},
        }

    def create(self, validated_data):
        request = self.context['request']
        subject = request.query_params.get('subject')
        name = validated_data.get('name')
        schema = validated_data.get('schema')
        is_visible = validated_data.get('is_visible')

        tenant = self.context['tenant']

        o: CustomField = CustomField.valid_objects.create(
            tenant=tenant,
            name=name,
            subject=subject,
            schema=schema,
            is_visible=is_visible,
        )

        return o


class NativeFieldSerializer(BaseDynamicFieldModelSerializer):
    '''
    serializer for NativeField
    '''

    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:  # pylint: disable=missing-docstring

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
                    raise ValidationError(
                        {
                            'is_visible': [
                                f"this file can't be changed for `{instance.name}`"
                            ]
                        }
                    )

        return super().update(instance, validated_data)


class PrivacyNoticeSerializer(BaseDynamicFieldModelSerializer):
    content = create_html_field(serializers.CharField)(hint=_("隐私声明内容"))

    class Meta:
        model = PrivacyNotice

        fields = ('title', 'content', 'is_active')

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.content = validated_data.get('content')
        instance.is_active = validated_data.get('is_active')
        instance.save()
        return instance


class PasswordComplexitySerializer(BaseDynamicFieldModelSerializer):
    regular = serializers.CharField(label=_('正则表达式'))
    is_apply = serializers.BooleanField(label=_('是否应用'))
    title = serializers.CharField(label=_('标题'))

    class Meta:
        model = PasswordComplexity

        fields = (
            'uuid',
            'regular',
            'is_apply',
            'title',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
        }

    def create(self, validated_data):
        tenant_uuid = self.context['request'].query_params.get('tenant')
        if tenant_uuid:
            tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        else:
            tenant = None
        regular = validated_data.get('regular')
        is_apply = validated_data.get('is_apply')
        title = validated_data.get('title')
        complexity = PasswordComplexity()
        complexity.tenant = tenant
        complexity.regular = regular
        complexity.is_apply = is_apply
        complexity.title = title
        complexity.save()
        if is_apply is True:
            PasswordComplexity.active_objects.filter(tenant=tenant).exclude(
                id=complexity.id
            ).update(is_apply=False)
        return complexity

    def update(self, instance, validated_data):
        tenant_uuid = self.context['request'].query_params.get('tenant')
        if tenant_uuid:
            tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        else:
            tenant = None
        is_apply = validated_data.get('is_apply')
        if is_apply is True:
            PasswordComplexity.active_objects.filter(tenant=tenant).exclude(
                id=instance.id
            ).update(is_apply=False)
        instance.__dict__.update(validated_data)
        instance.save()
        return instance

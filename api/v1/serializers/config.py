#!/usr/bin/env python3
from rest_framework import serializers
from inventory.models import CustomField, NativeField
from rest_framework.exceptions import ValidationError
from common.serializer import BaseDynamicFieldModelSerializer


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

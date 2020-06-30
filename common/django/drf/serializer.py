from collections import OrderedDict

from django.conf import settings
from rest_framework import serializers
from rest_framework.relations import PKOnlyObject
from rest_framework.fields import SkipField
from rest_framework.fields import Field


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        if getattr(settings, 'TESTING', False):
            # Drop any field about id if TESTING
            pk_fields = set([
                'id',
                'user_id',
                'dept_id',
                'group_id',
                'app_group_id',
                'perm_id',
            ])
            for pk_field in pk_fields:
                field = self.fields.get(pk_field, None)
                if field and isinstance(field, Field) and field.read_only:
                    self.fields.pop(pk_field, None)


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class IgnoreNoneMix(serializers.Serializer):
    '''
    ignore all None object(serialized by ModelSerializer)
    '''
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                # ret[field.field_name] = None
                if isinstance(field, serializers.ModelSerializer):
                    continue
                else:
                    ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class WritableSerializerMethodField(serializers.SerializerMethodField):
    '''
    可写的SerializerMethodField
    '''
    def __init__(self, method_name=None, **kwargs):
        self.method_name = method_name
        self.setter_method_name = kwargs.pop('setter_method_name', None)
        self.deserializer_field = kwargs.pop('deserializer_field')
        self.field_name = ''
        if 'read_only' not in kwargs:
            kwargs['read_only'] = False

        kwargs['source'] = '*'
        super(serializers.SerializerMethodField, self).__init__(**kwargs)

    def bind(self, field_name, parent):
        self.field_name = field_name
        retval = super().bind(field_name, parent)
        if not self.setter_method_name:
            self.setter_method_name = f'set_{field_name}'

        return retval

    def to_internal_value(self, data):
        value = self.deserializer_field.to_internal_value(data)
        method = getattr(self.parent, self.setter_method_name)
        method(value)
        return {self.field_name: value}

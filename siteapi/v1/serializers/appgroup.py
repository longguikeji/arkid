"""
serializers for app group
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from common.django.drf.serializer import DynamicFieldsModelSerializer, IgnoreNoneMix
from oneid_meta.models import AppGroup
from siteapi.v1.serializers import AppLiteSerializer
from siteapi.v1.serializers.node import NodeSerialzierMixin


class AppGroupSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    """
    Serializer for App Group with basic info
    """

    app_group_id = serializers.IntegerField(source='id', read_only=True)
    node_uid = serializers.CharField(read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = AppGroup
        fields = (
            'app_group_id',
            'node_uid',
            'uid',
            'name',
            'remark',
        )


class AppGroupListSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for App Group children
    """

    app_groups = AppGroupSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = AppGroup
        fields = ('app_groups', )


class AppGroupDetailSerializer(AppGroupSerializer):
    """
    app group info with parent_uid
    """
    class Meta:    # pylint: disable=missing-docstring
        model = AppGroup

        fields = (
            'parent_uid',
            'parent_node_uid',
            'parent_name',
            'app_group_id',
            'node_uid',
            'uid',
            'name',
            'remark',
            'visibility',
            'node_scope',
            'user_scope',
        )

    def create(self, validated_data):
        """
        create app group
        """
        app_group = AppGroup.objects.create(**validated_data)
        return app_group

    def update(self, instance, validated_data):
        """
        update app group
        """
        app_group = instance
        uid = validated_data.pop('uid', '')
        if uid and uid != app_group.uid:
            raise ValidationError({'uid': ['this field is immutable']})
        app_group.__dict__.update(validated_data)
        app_group.save(update_fields=validated_data.keys())
        return app_group

    def validate_uid(self, value):
        """
        校验uid唯一
        """
        exclude = {'pk': self.instance.pk} if self.instance else {}
        if self.Meta.model.valid_objects.filter(uid=value).exclude(**exclude).exists():
            raise ValidationError('this value has been used')
        return value

    def validate_node_scope(self, value):    # pylint: disable=no-self-use
        """
        must be list
        """
        if value and not isinstance(value, list):
            raise ValidationError({'node_scope': ['this field must be list']})
        return value

    def validate_user_scope(self, value):    # pylint: disable=no-self-use
        """
        must be list
        """
        if value and not isinstance(value, list):
            raise ValidationError({'user_scope': ['this field must be list']})
        return value


class AppGroupTreeSerializer(DynamicFieldsModelSerializer, NodeSerialzierMixin):
    """
    应用分组结构树，包括子应用分组
    """
    node_type = 'app_group'

    info = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    app_groups = serializers.SerializerMethodField()
    nodes = serializers.SerializerMethodField()

    visible = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        if kwargs.get('many', False):
            raise ValueError('not support many=True')

        super().__init__(*args, **kwargs)

        if not self.context.get('app_required', False):
            self.fields.pop('apps')

        self._user = self.context['request'].user
        self._visible = False    # 该节点对该用户是否可见，仅指判定结果
        if self.context.get('read_all', False):
            self._visible = True
        else:
            if self.context.get('user_identity', '') == 'manager':
                self._visible = self.instance.is_open_to_manager(self._user) if self.instance else False
            else:
                self._visible = self.instance.is_open_to_employee(self._user) if self.instance else False

        url_name = self.context.get('url_name', '')
        if not url_name:
            from django.urls import resolve    # pylint: disable=import-outside-toplevel
            url_name = resolve(self.context['request'].path_info).url_name
        if 'app_group' in url_name:
            self.children_name = 'app_groups'
            self.fields.pop('nodes')
        else:
            self.children_name = 'nodes'
            self.fields.pop('app_groups')

    class Meta:    # pylint: disable=missing-docstring
        model = AppGroup

        fields = (
            'info',
            'apps',
            'app_groups',
            'nodes',
            'visible',
        )

    def get_visible(self, instance):    # pylint: disable=unused-argument
        """
        该节点对该用户是否可见
        """
        return self._visible

    def get_info(self, instance):
        """
        若不可见则只返回基本信息
        """
        if self._visible:
            return AppGroupSerializer(instance).data
        return {
        # 'group_id': instance.id,
            'node_uid': instance.node_uid,
            'node_subject': instance.node_subject,
            'uid': instance.uid,
            'name': instance.name,
        }

    def get_users(self, instance):
        """
        若不可见则不返回应用
        """
        if self._visible:
            return AppLiteSerializer(instance.users, many=True).data
        return []

    def get_app_groups(self, instance):
        """
        下属应用分组
        """
        return [self.__class__(node, context=self.context).data for node in instance.children]

    def get_nodes(self, instance):
        '''
        下属节点
        '''
        return self.get_app_groups(instance)

'''
serializers for group
'''
# pylint: disable=import-outside-toplevel
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from common.django.drf.serializer import (
    DynamicFieldsModelSerializer, )
from common.django.drf.serializer import IgnoreNoneMix

from oneid_meta.models import (
    Group,
    DingGroup,
    ManagerGroup,
    Perm,
    GroupPerm,
    User,
    APP,
)
from oneid_meta.models.mixin import TreeNode as Node
from siteapi.v1.serializers import UserLiteSerializer
from siteapi.v1.serializers.node import NodeSerialzierMixin


class DingGroupSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for DingGroup
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = DingGroup
        fields = (
            'uid',
            'data',
            'subject',
            'is_group',
        )


class ManagerGroupSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for ManagerGroup
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = ManagerGroup
        fields = (
            'nodes',
            'users',
            'apps',
            'perms',
            'scope_subject',
        )

    def create(self, validated_data):
        '''
        创建子管理员组并分配权限
        '''
        perms = []
        for perm_uid in validated_data.get('perms', []):
            perm = Perm.valid_objects.filter(uid=perm_uid).first()
            if not perm:
                raise ValidationError({'perms': f'{perm_uid} not found'})
            perms.append(perm)

        manager_group = super().create(validated_data)
        group = manager_group.group

        for perm in perms:
            group_perm = GroupPerm.get(group, perm)
            group_perm.permit()

        return manager_group

    def update(self, instance, validated_data):
        '''
        更新子管理员组并重置权限
        '''
        previous_perm_uids = instance.perms
        manager_group = super().update(instance, validated_data)

        perm_uids = validated_data.get('perms', None)
        if perm_uids is None:
            return manager_group

        next_perms = set()
        for perm_uid in validated_data['perms']:
            perm = Perm.valid_objects.filter(uid=perm_uid).first()
            if not perm:
                raise ValidationError({'perms': f'{perm_uid} not found'})
            next_perms.add(perm)

        previous_perms = set()
        for perm_uid in previous_perm_uids:
            perm = Perm.valid_objects.filter(uid=perm_uid).first()
            if perm:
                previous_perms.add(perm)

        group = instance.group
        for perm in previous_perms - next_perms:
            group_perm = GroupPerm.get(group, perm)
            group_perm.boggle()
        for perm in next_perms - previous_perms:
            group_perm = GroupPerm.get(group, perm)
            group_perm.permit()

        return manager_group


class VerboseManagerGroupSerializer(DynamicFieldsModelSerializer):
    '''
    verbose serialzier for ManagerGroup
    '''

    nodes = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    apps = serializers.SerializerMethodField()
    perms = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = ManagerGroup
        fields = (
            'nodes',
            'users',
            'apps',
            'perms',
            'scope_subject',
        )

    @staticmethod
    def get_nodes(instance):
        '''
        管理节点范围
        '''
        if instance.scope_subject == 2:
            for node in Node.retrieve_nodes(instance.nodes):
                yield {
                    'node_uid': node.node_uid,
                    'node_subject': node.node_subject,
                    'name': node.name,
                }

    @staticmethod
    def get_users(instance):
        '''
        管理人员范围
        '''
        if instance.scope_subject == 2:
            for user in User.valid_objects.filter(username__in=instance.users):
                yield {
                    'name': user.name,
                    'username': user.username,
                }

    @staticmethod
    def get_apps(instance):
        '''
        管理应用范围
        '''
        for app in APP.valid_objects.filter(uid__in=instance.apps):
            yield {
                'uid': app.uid,
                'name': app.name,
            }

    @staticmethod
    def get_perms(instance):
        '''
        管理权限范围
        '''
        for perm in Perm.objects.filter(uid__in=instance.perms):
            yield {
                'uid': perm.uid,
                'name': perm.name,
            }

    def to_representation(self, instance):
        '''
        更新有效管理范围
        '''
        res = super().to_representation(instance)

        if instance.scope_subject == 2:
            res['nodes'] = list(res['nodes'])
            instance.nodes = [item['node_uid'] for item in res['nodes']]

            res['users'] = list(res['users'])
            instance.users = [item['username'] for item in res['users']]

        res['apps'] = list(res['apps'])
        instance.apps = [item['uid'] for item in res['apps']]

        res['perms'] = list(res['perms'])
        instance.perms = [item['uid'] for item in res['perms']]

        instance.save()

        return res


class GroupSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    '''
    Serializer for Group with basic info
    '''

    group_id = serializers.IntegerField(source='id', read_only=True)
    ding_group = DingGroupSerializer(many=False, required=False)
    manager_group = ManagerGroupSerializer(many=False, required=False)
    node_uid = serializers.CharField(read_only=True)
    node_subject = serializers.CharField(read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Group

        fields = (
            'group_id',
            'node_uid',
            'node_subject',
            'uid',
            'name',
            'remark',
            'accept_user',
            'ding_group',
            'manager_group',
        )


class GroupDetailSerializer(GroupSerializer):
    '''
    group info with parent_uid
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = Group

        fields = (
            'parent_uid',
            'parent_node_uid',
            'parent_name',
            'group_id',
            'node_uid',
            'node_subject',
            'uid',
            'name',
            'remark',
            'accept_user',
            'ding_group',
            'manager_group',
            'visibility',
            'node_scope',
            'user_scope',
        )

    def create(self, validated_data):
        '''
        create group
        create ding_group if provided
        create manager_group if provided
        '''
        ding_group_data = validated_data.pop('ding_group', None)
        manager_group_data = validated_data.pop('manager_group', None)
        group = Group.objects.create(**validated_data)

        if ding_group_data:
            ding_group_serializer = DingGroupSerializer(data=ding_group_data)
            ding_group_serializer.is_valid(raise_exception=True)
            ding_group_serializer.save(group=group)

        if manager_group_data:
            manager_group_serializer = ManagerGroupSerializer(data=manager_group_data)
            manager_group_serializer.is_valid(raise_exception=True)
            manager_group_serializer.save(group=group)

        return group

    def update(self, instance, validated_data):
        '''
        update group
        update/create ding_dept if provided
        '''
        group = instance
        ding_group_data = validated_data.pop('ding_group', None)
        manager_group_data = validated_data.pop('manager_group', None)

        if ding_group_data:
            if hasattr(group, 'ding_group'):
                ding_group_serializer = DingGroupSerializer(instance=instance.ding_group,
                                                            data=ding_group_data,
                                                            partial=True)
                ding_group_serializer.is_valid(raise_exception=True)
                ding_group_serializer.save()
            else:
                ding_group_serializer = DingGroupSerializer(data=ding_group_data)
                ding_group_serializer.is_valid(raise_exception=True)
                ding_group_serializer.save(group=group)

        if manager_group_data:
            if hasattr(group, 'manager_group'):
                manager_group_serializer = ManagerGroupSerializer(
                    instance=instance.manager_group,
                    data=manager_group_data,
                    partial=True,
                )
                manager_group_serializer.is_valid(raise_exception=True)
                manager_group_serializer.save()
            else:
                manager_group_serializer = ManagerGroupSerializer(data=manager_group_data)
                manager_group_serializer.is_valid(raise_exception=True)
                manager_group_serializer.save(group=group)

        uid = validated_data.pop('uid', '')
        if uid and uid != group.uid:
            raise ValidationError({'uid': ['this field is immutable']})

        group.__dict__.update(validated_data)
        group.save(update_fields=validated_data.keys())

        return group

    def validate_uid(self, value):
        '''
        校验uid唯一
        '''
        exclude = {'pk': self.instance.pk} if self.instance else {}
        if self.Meta.model.valid_objects.filter(uid=value).exclude(**exclude).exists():
            raise ValidationError('this value has been used')
        return value

    def validate_node_scope(self, value):    # pylint: disable=no-self-use
        '''
        must be list
        '''
        if value and not isinstance(value, list):
            raise ValidationError({'node_scope': ['this field must be list']})
        return value

    def validate_user_scope(self, value):    # pylint: disable=no-self-use
        '''
        must be list
        '''
        if value and not isinstance(value, list):
            raise ValidationError({'user_scope': ['this field must be list']})
        return value


class GroupWithVerboseManagerGroup(GroupDetailSerializer):
    '''
    group info with verbose manager group detail
    '''
    manager_group = VerboseManagerGroupSerializer()
    users = UserLiteSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Group
        fields = (
            'parent_uid',
            'parent_node_uid',
            'parent_name',
            'group_id',
            'node_uid',
            'node_subject',
            'uid',
            'name',
            'remark',
            'accept_user',
            'ding_group',
            'manager_group',
            'visibility',
            'node_scope',
            'user_scope',
            'users',
        )


class GroupListSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for Group children
    '''

    groups = GroupSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Group

        fields = ('groups', )


class ManagerGroupListSerializer(DynamicFieldsModelSerializer):
    '''
    serialzier for Group children with ManagerGroup
    '''
    groups = GroupWithVerboseManagerGroup(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Group

        fields = ('groups', )


class GroupTreeSerializer(DynamicFieldsModelSerializer, NodeSerialzierMixin):
    '''
    组结构树，包括子部门
    '''
    node_type = 'group'

    info = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    nodes = serializers.SerializerMethodField()

    visible = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        if kwargs.get('many', False):
            raise ValueError('not support many=True')

        super().__init__(*args, **kwargs)

        if not self.context.get('user_required', False):
            self.fields.pop('users')

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
            from django.urls import resolve
            url_name = resolve(self.context['request'].path_info).url_name
        if 'group' in url_name:
            self.children_name = 'groups'
            self.fields.pop('nodes')
        else:
            self.children_name = 'nodes'
            self.fields.pop('groups')

    class Meta:    # pylint: disable=missing-docstring
        model = Group

        fields = (
            'info',
            'users',
            'groups',
            'nodes',
            'visible',
        )

    def get_visible(self, instance):    # pylint: disable=unused-argument
        '''
        该节点对该用户是否可见
        '''
        return self._visible

    def get_info(self, instance):
        '''
        若不可见则只返回基本信息
        '''
        if self._visible:
            return GroupSerializer(instance).data
        return {
        # 'group_id': instance.id,
            'node_uid': instance.node_uid,
            'node_subject': instance.node_subject,
            'uid': instance.uid,
            'name': instance.name,
        }

    def get_users(self, instance):
        '''
        若不可见则不返回用户
        '''
        if self._visible:
            return UserLiteSerializer(instance.users, many=True).data
        return []

    def get_groups(self, instance):
        '''
        下属组
        '''
        return [self.__class__(node, context=self.context).data for node in instance.children]

    def get_nodes(self, instance):
        '''
        下属节点
        '''
        return self.get_groups(instance)

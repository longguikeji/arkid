'''
serializers for department
'''
from django.urls import resolve
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from common.django.drf.serializer import (
    DynamicFieldsModelSerializer, )
from common.django.drf.serializer import IgnoreNoneMix

from oneid_meta.models import Dept, DingDept, CustomDept
from siteapi.v1.serializers import UserLiteSerializer
from siteapi.v1.serializers.node import NodeSerialzierMixin


class DingDeptSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for DingDept
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = DingDept

        fields = (
            'uid',
            'data',
        )


class DeptLiteSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    '''
    Serializer for Dept with basic info
    '''
    dept_id = serializers.IntegerField(source='id', read_only=True)
    node_uid = serializers.CharField(read_only=True)
    node_subject = serializers.CharField(read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Dept

        fields = (
            'dept_id',
            'node_uid',
            'node_subject',
            'uid',
            'name',
            'remark',
        )

class CustomDeptSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CustomDept
        fields = ('data',)

class DeptSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    '''
    Serializer for Dept with basic info & *_dept
    '''

    dept_id = serializers.IntegerField(source='id', read_only=True)
    ding_dept = DingDeptSerializer(many=False, required=False)
    node_uid = serializers.CharField(read_only=True)
    node_subject = serializers.CharField(read_only=True)
    custom = CustomDeptSerializer(source='custom_dept', many=False, required=False, allow_null=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Dept

        fields = (
            'dept_id',
            'node_uid',
            'node_subject',
            'uid',
            'name',
            'remark',
            'custom',
            'ding_dept',
        )


class DeptDetailSerializer(DeptSerializer):
    '''
    dept info with parent_uid
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = Dept

        fields = (
            'parent_uid',
            'parent_node_uid',
            'parent_name',
            'dept_id',
            'node_uid',
            'node_subject',
            'uid',
            'name',
            'remark',
            'custom',
            'ding_dept',
            'visibility',
            'node_scope',
            'user_scope',
        )

    def create(self, validated_data):
        '''
        create dept
        create ding_dept if provided
        '''
        custom_dept_data = validated_data.pop('custom_dept',None)
        ding_dept_data = validated_data.pop('ding_dept', None)
        dept = Dept.objects.create(**validated_data)

        if custom_dept_data:
            custom_dept_serialier = CustomDeptSerializer(data=custom_dept_data)
            custom_dept_serialier.is_valid(raise_exception=True)
            custom_dept_serialier.save(dept=dept)

        if ding_dept_data:
            ding_dept_serialier = DingDeptSerializer(data=ding_dept_data)
            ding_dept_serialier.is_valid(raise_exception=True)
            ding_dept_serialier.save(dept=dept)

        return dept

    def update(self, instance, validated_data):
        '''
        update dept
        update/create ding_dept if provided
        '''
        dept = instance
        custom_dept_data = validated_data.pop('custom_dept', None)
        ding_dept_data = validated_data.pop('ding_dept', None)

        if custom_dept_data:
            if hasattr(dept, 'custom_dept'):
                custom_dept_serializer = CustomDeptSerializer(instance=instance.custom_dept,
                                                          data=custom_dept_data,
                                                          partial=True)
                custom_dept_serializer.is_valid(raise_exception=True)
                custom_dept_serializer.save()
            else:
                custom_dept_serializer = CustomDeptSerializer(data=custom_dept_data)
                custom_dept_serializer.is_valid(raise_exception=True)
                custom_dept_serializer.save(dept=dept)

        if ding_dept_data:
            if hasattr(dept, 'ding_dept'):
                ding_dept_serializer = DingDeptSerializer(instance=instance.ding_dept,
                                                          data=ding_dept_data,
                                                          partial=True)
                ding_dept_serializer.is_valid(raise_exception=True)
                ding_dept_serializer.save()
            else:
                ding_dept_serializer = DingDeptSerializer(data=ding_dept_data)
                ding_dept_serializer.is_valid(raise_exception=True)
                ding_dept_serializer.save(dept=dept)

        uid = validated_data.pop('uid', '')
        if uid and uid != dept.uid:
            raise ValidationError({'uid': ['this field is immutable']})

        visibility = validated_data.get('visibility', None)
        if visibility != 4:    # 除 指定人、节点外的其他情况
            validated_data['user_scope'] = []
            validated_data['node_scope'] = []

        dept.__dict__.update(validated_data)
        dept.save(update_fields=validated_data.keys())
        return dept

    def validate_uid(self, value):
        '''
        校验uid唯一
        '''
        exclude = {'pk': self.instance.pk} if self.instance else {}
        if self.Meta.model.valid_objects.filter(uid=value).exclude(**exclude).exists():
            raise ValidationError(['this value has be used'])
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


class DeptListSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for Groups with basic info
    '''

    depts = DeptSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = Dept

        fields = ('depts', )

import time
from oneid_meta.models.group import GroupMember, ManagerGroup
from oneid_meta.models.dept import DeptMember

class DeptCash:
    
    dept_tree = {}
    dept_hash = {}
    visible_dept = []
    @staticmethod
    def clear():
        DeptCash.dept_hash = {}
        DeptCash.dept_tree = {}
        DeptCash.visible_dept = []
        
    @staticmethod
    def init():
        if not DeptCash.dept_hash:
            dept_hash = {}
            dept_tree = {}
            ds = Dept.valid_objects.all()
            for d in ds:
                dept_hash[d.id] = d
                if d.parent_id:
                    if not dept_tree.get(d.parent_id):
                        dept_tree[d.parent_id] = [d.id]
                    else:
                        dept_tree[d.parent_id].append(d.id)
                    
            
            DeptCash.dept_hash = dept_hash
            DeptCash.dept_tree = dept_tree
        return True
    @staticmethod
    def get_dept_children(dept_uid):
        DeptCash.init()
        return DeptCash.dept_tree.get(dept_uid)

    @staticmethod
    def get_dept_list(dept_id):
        DeptCash.init()
        dids = DeptCash.get_dept_children(dept_id)
        if not dids:
            return []
        depts = dids
        # print('dids', dids)
        for did in dids:
            depts += DeptCash.get_dept_list(did)
        return depts

    @staticmethod
    def get_dept(dept_id):
        DeptCash.init()
        return DeptCash.dept_hash.get(dept_id)
    
    @staticmethod
    def init_visible(user):
        if not DeptCash.visible_dept:
            mgs = ManagerGroup.valid_objects.filter(group__in=GroupMember.valid_objects.values('owner').filter(user=user).distinct())
            for mg in mgs:
                depts = []
                if mg.scope_subject == 1: # 查出user所在的所有组
                    dd = Dept.valid_objects.filter(id__in=DeptMember.valid_objects.values('owner').filter(user=user).distinct())
                    depts += dd
                    ids = []
                    for d in dd:
                        ids += DeptCash.get_dept_list(d.id)
                    for i in ids:
                        depts.append(DeptCash.get_dept(i))
                else:
                    uids = []
                    for node in mg.nodes:
                        uids.append(node.replace('d_', ''))
                    depts = Dept.valid_objects.filter(uid__in=uids)
                DeptCash.visible_dept += depts
            # print(DeptCash.visible_dept)

    @staticmethod
    def get_dept_visible(dept,user):
        DeptCash.init_visible(user)
        for d in DeptCash.visible_dept:
            if d.id == dept.id:
                return True
        return False
    

class DeptTreeSerializer(DynamicFieldsModelSerializer, NodeSerialzierMixin):

    '''
    部门结构树，包括子部门和成员
    '''

    node_type = 'dept'

    info = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    depts = serializers.SerializerMethodField()
    nodes = serializers.SerializerMethodField()

    visible = serializers.SerializerMethodField()
    has_children = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        # TODO: requets not exists

        if kwargs.get('many', False):
            raise ValueError('not support many=True')

        super().__init__(*args, **kwargs)

        if not self.context.get('user_required', False):
            self.fields.pop('users')

        self._user = self.context['request'].user
        self._visible = False    # 该节点对该用户是否可见，仅指判定结果
        if self.context.get('read_all', False):
            self._visible = True
        elif self._user.is_admin:
            self._visible = True
        else:
            if self.context.get('user_identity', '') == 'manager':
                self._visible = DeptCash.get_dept_visible(self.instance, self._user) if self.instance else False
                # self._visible = self.instance.is_open_to_manager(self._user) if self.instance else False
            else:
                self._visible = self.instance.is_open_to_employee(self._user) if self.instance else False


        url_name = self.context.get('url_name', '')
        if not url_name:
            url_name = resolve(self.context['request'].path_info).url_name
        if 'dept' in url_name:
            self.children_name = 'depts'
            self.fields.pop('nodes')
        else:
            self.children_name = 'nodes'
            self.fields.pop('depts')
        self.return_child_depts = self.context.get('return_child_depts', True)


    class Meta:    # pylint: disable=missing-docstring
        model = Dept

        fields = (
            'info',
            'users',
            'depts',
            'nodes',
            'visible',
            'has_children'
        )

    def get_visible(self, instance):    # pylint: disable=unused-argument
        '''
        该节点对该用户是否可见
        '''
        return self._visible

    def get_info(self, instance):
        '''
        只返回基本信息
        '''
        # if self._visible:
            # return DeptSerializer(instance).data
        return {
            'dept_id': instance.id,
            'node_uid': instance.node_uid,
            'node_subject': instance.node_subject,
            'uid': instance.uid,
            'name': instance.name,
            'remark': instance.remark,
        }

    def get_users(self, instance):
        '''
        若不可见则不返回用户
        '''
        if self._visible:
            return UserLiteSerializer(instance.users, many=True).data
        return []

    def get_has_children(self, instance):
        child_ids = DeptCash.get_dept_children(instance.id)
        if child_ids:
            return True
        else:
            return False

    def get_depts(self, instance):
        '''
        下属部门
        '''
        # redata = [self.__class__(node, context=self.context).data for node in instance.children]
        if not self.return_child_depts:
            return []
        children = []
        child_ids = DeptCash.get_dept_children(instance.id)
        if not child_ids:
            return []
        
        for child_id in child_ids:
            children.append(DeptCash.get_dept(child_id))

        self.context['return_child_depts'] = False
        redata = [self.__class__(node, context=self.context).data for node in children]
        return redata
        # return [node for node in instance.children]

    def get_nodes(self, instance):
        '''
        下属节点
        '''
        return self.get_depts(instance)

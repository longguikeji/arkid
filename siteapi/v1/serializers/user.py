'''
serializers for user
'''
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from oneid_meta.models import (
    User,
    DingUser,
    PosixUser,
    Dept,
    Group,
    UserPerm,
    CustomUser,
    NativeField,
)
from common.django.drf.serializer import DynamicFieldsModelSerializer
from common.django.drf.serializer import IgnoreNoneMix
from siteapi.v1.serializers.dept import DeptSerializer
from siteapi.v1.serializers.group import GroupSerializer


class CustomUserSerailizer(DynamicFieldsModelSerializer):
    '''
    custom user info
    '''

    pretty = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring
        model = CustomUser

        fields = ('data', 'pretty')

        extra_kwargs = {'pretty': {'read_only': True}}

    def get_pretty(self, instance):    # pylint: disable=no-self-use
        '''
        前端友好的输出
        '''
        return instance.pretty(visible_only=True)


class AdvanceCustomUserSerializer(CustomUserSerailizer):
    '''
    custom user info include all fields
    '''
    def get_pretty(self, instance):
        return instance.pretty(visible_only=False)


class UserProfileSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    '''
    user profile
    '''

    custom_user = CustomUserSerailizer(many=False, required=False)
    visible_fields = serializers.SerializerMethodField()
    depts = serializers.SerializerMethodField()

    class Meta:    # pylint: disable=missing-docstring

        model = User

        fields = (
            'username',
            'name',
            'email',
            'mobile',
            'employee_number',
            'gender',
            'avatar',
            'depts',
            'custom_user',
            'visible_fields',    # 按需使用，不在该列表中不意味着不展示，反例如`avatar`
            'private_email',
            'position',
        )

        read_only_fields = ('user_id', 'username', 'mobile', 'depts', 'visible_fields')

    @staticmethod
    def get_visible_fields(instance):    # pylint: disable=unused-argument
        '''
        哪些字段可见
        '''
        for field in NativeField.valid_objects.filter(subject='user', is_visible=True):
            yield field.key

    @staticmethod
    def get_depts(instance):
        '''
        所属部门列表，用于展示
        '''
        for dept in instance.depts:
            yield {'uid': dept.uid, 'name': dept.name}

    def update(self, instance, validated_data):
        user = instance
        custom_user_data = validated_data.pop('custom_user', None)
        if custom_user_data:
            if hasattr(user, 'custom_user'):
                custom_user_serailizer = CustomUserSerailizer(user.custom_user, data=custom_user_data, partial=True)
                custom_user_serailizer.is_valid(raise_exception=True)
                custom_user_serailizer.save()
            else:
                custom_user_serailizer = CustomUserSerailizer(data=custom_user_data)
                custom_user_serailizer.is_valid(raise_exception=True)
                custom_user_serailizer.save(user=user)
        user.__dict__.update(validated_data)
        user.save()
        return user


class DingUserSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for DingUser
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = DingUser

        fields = (
            'uid',
            'account',
            'data',
        )


class PosixUserSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for PosixUser
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = PosixUser

        fields = (
            'uid',
            'gid',
            'home',
            'pub_key',
        )


class UserLiteSerializer(DynamicFieldsModelSerializer):
    '''
    lite Serializer for User
    '''
    class Meta:    # pylint: disable=missing-docstring

        model = User

        fields = (
            'username',
            'name',
        )


class UserSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    '''
    Serializer for User
    '''

    ding_user = DingUserSerializer(many=False, required=False)
    posix_user = PosixUserSerializer(many=False, required=False)
    custom_user = AdvanceCustomUserSerializer(many=False, required=False)
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:    # pylint: disable=missing-docstring

        model = User

        fields = (
            'user_id',
            'username',
            'name',
            'email',
            'mobile',
            'employee_number',
            'gender',
            'avatar',
            'private_email',
            'position',
            'ding_user',
            'posix_user',
            'custom_user',
            'is_settled',
            'is_manager',
            'is_admin',
            'origin_verbose',
        )

    def create(self, validated_data):
        '''
        create user
        create ding_user if provided
        create posix_user if provided
        create custom_user if provided
        '''
        ding_user_data = validated_data.pop('ding_user', None)
        posix_user_data = validated_data.pop('posix_user', None)
        custom_user_data = validated_data.pop('custom_user', None)

        user = User.objects.create(**validated_data)

        if ding_user_data:
            ding_user_serializer = DingUserSerializer(data=ding_user_data)
            ding_user_serializer.is_valid(raise_exception=True)
            ding_user_serializer.save(user=user)

        if posix_user_data:
            posix_user_serializer = PosixUserSerializer(data=posix_user_data)
            posix_user_serializer.is_valid(raise_exception=True)
            posix_user_serializer.save(user=user)

        if custom_user_data:
            custom_user_serializer = CustomUserSerailizer(data=custom_user_data)
            custom_user_serializer.is_valid(raise_exception=True)
            custom_user_serializer.save(user=user)

        return user

    def update(self, instance, validated_data):
        '''
        update user
        update/create ding_user if provided
        update/create posix_user if provided
        update/create custom_user if provided
        '''
        user = instance
        ding_user_data = validated_data.pop('ding_user', None)
        posix_user_data = validated_data.pop('posix_user', None)
        custom_user_data = validated_data.pop('custom_user', None)

        if ding_user_data:
            if hasattr(user, 'ding_user'):
                ding_user_serializer = DingUserSerializer(user.ding_user, data=ding_user_data, partial=True)
                ding_user_serializer.is_valid(raise_exception=True)
                ding_user_serializer.save()
            else:
                ding_user_serializer = DingUserSerializer(data=ding_user_data)
                ding_user_serializer.is_valid(raise_exception=True)
                ding_user_serializer.save(user=user)

        if posix_user_data:
            if hasattr(user, 'posix_user'):
                posix_user_serializer = PosixUserSerializer(user.posix_user, data=posix_user_data, partial=True)
                posix_user_serializer.is_valid(raise_exception=True)
                posix_user_serializer.save()
            else:
                posix_user_serializer = PosixUserSerializer(data=posix_user_data)
                posix_user_serializer.is_valid(raise_exception=True)
                posix_user_serializer.save(user=user)

        if custom_user_data:
            if hasattr(user, 'custom_user'):
                custom_user_serailizer = CustomUserSerailizer(user.custom_user, data=custom_user_data, partial=True)
                custom_user_serailizer.is_valid(raise_exception=True)
                custom_user_serailizer.save()
            else:
                custom_user_serailizer = CustomUserSerailizer(data=custom_user_data)
                custom_user_serailizer.is_valid(raise_exception=True)
                custom_user_serailizer.save(user=user)

        username = validated_data.pop('username', '')
        if username and username != user.username:
            raise ValidationError({'username': ['this field is immutable']})

        user.__dict__.update(validated_data)
        user.save()
        return user

    def validate_username(self, value):
        '''
        校验username唯一
        '''
        value = value.strip(' ')
        if not re.match(r'^[a-z0-9]+$', value):
            raise ValidationError('invalid')
        exclude = {'pk': self.instance.pk} if self.instance else {}
        if self.Meta.model.valid_objects.filter(username=value).exclude(**exclude).exists():
            raise ValidationError(['existed'])
        return value


class UserWithPermSerializer(UserSerializer):
    '''
    user info with perms
    '''
    perms = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    uuid = serializers.UUIDField(format='hex')

    class Meta:    # pylint: disable=missing-docstring

        model = User

        fields = (
            'uuid',
            'user_id',
            'username',
            'name',
            'email',
            'mobile',
            'employee_number',
            'gender',
            'ding_user',
            'posix_user',
            'perms',
            'avatar',
            'roles',
            'private_email',
            'position',
            'custom_user',
            'is_settled',
            'is_manager',
            'is_admin',
            'origin_verbose',
        )

    def get_perms(self, obj):    # pylint: disable=no-self-use
        '''
        返回所有拥有的权限的uid
        '''
        filters = {
            'owner__username': obj.username,
            'value': True,
        }
        return [
            item['perm__uid'] for item in \
                UserPerm.valid_objects.filter(**filters).order_by('perm').values('perm__uid')
        ]

    def get_roles(self, obj):    # pylint: disable=no-self-use
        '''
        特殊角色。角色之间独立，无包含关系。
        - admin - 主管理员，不保证admin一定是manager
        - manager - 子管理员
        '''
        if obj.is_admin:
            yield 'admin'
        if obj.is_manager:
            yield 'manager'


class UserListSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for Users
    '''
    users = UserSerializer(many=True)

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = ('users', )


class EmployeeSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for employee with user info, groups basic info, depts basic info
    '''

    user = UserSerializer(source='*')
    groups = GroupSerializer(many=True, read_only=True)
    depts = DeptSerializer(many=True, read_only=True)

    nodes = serializers.SerializerMethodField()

    group_uids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),
                                                    many=True,
                                                    pk_field='uid',
                                                    write_only=True,
                                                    required=False)
    dept_uids = serializers.PrimaryKeyRelatedField(queryset=Dept.objects.all(),
                                                   many=True,
                                                   pk_field='uid',
                                                   write_only=True,
                                                   required=False)

    node_uids = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all(),
                                                   many=True,
                                                   pk_field='uid',
                                                   write_only=True,
                                                   required=False)

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'group_uids',
            'dept_uids',
            'node_uids',
            'user',
            'groups',
            'depts',
            'nodes',
        )

    def get_nodes(self, obj):    # pylint: disable=no-self-use
        '''
        groups + nodes
        '''
        for item in self.get_groups(obj):
            yield item

        for item in DeptSerializer(obj.depts, many=True).data:
            yield item

    def get_groups(self, obj):    # pylint: disable=no-self-use
        '''
        出于业务需要，extern 不予展示
        '''
        return GroupSerializer([group for group in obj.groups if group.uid != 'extern'], many=True).data

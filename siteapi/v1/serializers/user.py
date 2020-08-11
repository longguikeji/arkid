# pylint: disable=too-many-lines
'''
serializers for user
'''
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from oneid_meta.models import (
    User,
    DingUser,
    PosixUser,
    UserPerm,
    CustomUser,
    NativeField,
    SubAccount,
    WechatUser,
    GithubUser,
)
from common.django.drf.serializer import DynamicFieldsModelSerializer
from common.django.drf.serializer import IgnoreNoneMix
from siteapi.v1.serializers.dept import DeptLiteSerializer
from siteapi.v1.serializers.group import GroupLiteSerializer
from siteapi.v1.serializers.utils import username_valid


class CustomUserSerializer(DynamicFieldsModelSerializer):
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


class AdvanceCustomUserSerializer(CustomUserSerializer):
    '''
    custom user info include all fields
    '''
    def get_pretty(self, instance):
        return instance.pretty(visible_only=False)


class UserProfileSerializer(DynamicFieldsModelSerializer, IgnoreNoneMix):
    '''
    user profile
    '''

    custom_user = CustomUserSerializer(many=False, required=False)
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
            'remark',
        )

        read_only_fields = ('user_id', 'username', 'mobile', 'depts', 'visible_fields')

    @staticmethod
    def get_visible_fields(instance):    # pylint: disable=unused-argument
        '''
        哪些字段可见
        '''
        if instance.is_intra:
            return [field.key for field in NativeField.valid_objects.filter(subject='user', is_visible=True)]

        return [field.key for field in NativeField.valid_objects.filter(subject='extern_user', is_visible=True)]

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
                custom_user_serializer = CustomUserSerializer(user.custom_user, data=custom_user_data, partial=True)
                custom_user_serializer.is_valid(raise_exception=True)
                custom_user_serializer.save()
            else:
                custom_user_serializer = CustomUserSerializer(data=custom_user_data)
                custom_user_serializer.is_valid(raise_exception=True)
                custom_user_serializer.save(user=user)
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


class WechatUserSerializer(DynamicFieldsModelSerializer):
    '''
    Serializer for WechatUser
    '''
    class Meta:    # pylint: disable=missing-docstring
        model = WechatUser

        fields = ('unionid', )


class GithubUserSerializer(DynamicFieldsModelSerializer):
    """
    Serializer for Github User
    """
    class Meta:    # pylint: disable=missing-docstring
        model = GithubUser

        fields = ('github_user_id', )


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

    ding_user = DingUserSerializer(many=False, required=False, allow_null=True)
    # posix_user = PosixUserSerializer(many=False, required=False, allow_null=True)
    wechat_user = WechatUserSerializer(many=False, required=False, allow_null=True)
    github_user = GithubUserSerializer(many=False, required=False, allow_null=True)
    custom_user = AdvanceCustomUserSerializer(many=False, required=False, allow_null=True)
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
            'custom_user',
            'wechat_user',
            'github_user',
            'is_settled',
            'is_manager',
            'is_admin',
            'origin_verbose',
            'hiredate',
            'remark',
            'created',
            'last_active_time',
            'is_extern_user',
            'require_reset_password',
            'has_password',
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
        wechat_user_data = validated_data.pop('wechat_user', None)

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
            custom_user_serializer = CustomUserSerializer(data=custom_user_data)
            custom_user_serializer.is_valid(raise_exception=True)
            custom_user_serializer.save(user=user)

        if wechat_user_data:
            wechat_user_serializer = WechatUserSerializer(data=wechat_user_data)
            wechat_user_serializer.is_valid(raise_exception=True)
            wechat_user_serializer.save(user=user)

        return user

    def update(self, instance, validated_data):    # pylint: disable=too-many-statements,too-many-branches
        '''
        update user
        update/create ding_user if provided
        update/create posix_user if provided
        update/create custom_user if provided
        '''
        user = instance

        if 'ding_user' in validated_data:
            ding_user_data = validated_data.pop('ding_user')
            if hasattr(user, 'ding_user'):
                ding_user_serializer = DingUserSerializer(user.ding_user, data=ding_user_data, partial=True)
                ding_user_serializer.is_valid(raise_exception=True)
                ding_user_serializer.save()
            else:
                ding_user_serializer = DingUserSerializer(data=ding_user_data)
                ding_user_serializer.is_valid(raise_exception=True)
                ding_user_serializer.save(user=user)

        if 'posix_user' in validated_data:
            posix_user_data = validated_data.pop('posix_user')
            if hasattr(user, 'posix_user'):
                posix_user_serializer = PosixUserSerializer(user.posix_user, data=posix_user_data, partial=True)
                posix_user_serializer.is_valid(raise_exception=True)
                posix_user_serializer.save()
            else:
                posix_user_serializer = PosixUserSerializer(data=posix_user_data)
                posix_user_serializer.is_valid(raise_exception=True)
                posix_user_serializer.save(user=user)

        if 'custom_user' in validated_data:
            custom_user_data = validated_data.pop('custom_user')
            if hasattr(user, 'custom_user'):
                custom_user_serializer = CustomUserSerializer(user.custom_user, data=custom_user_data, partial=True)
                custom_user_serializer.is_valid(raise_exception=True)
                custom_user_serializer.save()
            else:
                custom_user_serializer = CustomUserSerializer(data=custom_user_data)
                custom_user_serializer.is_valid(raise_exception=True)
                custom_user_serializer.save(user=user)

        if 'wechat_user' in validated_data:
            wechat_user_data = validated_data.pop('wechat_user')
            if hasattr(user, 'wechat_user'):
                if wechat_user_data is None:    # 解绑
                    user.wechat_user.kill()
                    user.wechat_user = None
                else:
                    wechat_user_serializer = WechatUserSerializer(user.wechat_user, data=wechat_user_data, partial=True)
                    wechat_user_serializer.is_valid(raise_exception=True)
                    wechat_user_serializer.save()
            else:
                if wechat_user_data:
                    wechat_user_serializer = WechatUserSerializer(data=wechat_user_data)
                    wechat_user_serializer.is_valid(raise_exception=True)
                    wechat_user_serializer.save(user=user)

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
        if not username_valid(value):
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
            'ding_user',
            'perms',
            'avatar',
            'roles',
            'private_email',
            'position',
            'custom_user',
            'is_settled',
            'is_manager',
            'is_admin',
            'is_extern_user',
            'origin_verbose',
            'require_reset_password',
            'has_password',
        )

    def get_perms(self, obj):    # pylint: disable=no-self-use
        '''
        返回所有拥有的权限的uid
        '''
        filters = {
            'owner__username': obj.username,
            'value': True,
        }
        app = self.context.get('app', None)
        if app:
            # 当明确 app 时，只返回拥有的此app内的权限，且去除 app 前缀
            prefix = 'app_{}_'.format(app.uid)
            filters.update(perm__uid__startswith=prefix)

        queryset = UserPerm.valid_objects.filter(**filters).order_by('perm').values('perm__uid')
        if app:
            return [item['perm__uid'].replace(prefix, '') for item in queryset]

        return [item['perm__uid'] for item in queryset]

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


class EmployeeSerializer(UserSerializer):
    '''
    Serializer for User with Nodes
    '''

    nodes = serializers.SerializerMethodField()

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
            'custom_user',
            'wechat_user',
            'github_user',
            'is_settled',
            'is_manager',
            'is_admin',
            'origin_verbose',
            'hiredate',
            'remark',
            'nodes',
            'created',
            'last_active_time',
            'is_extern_user',
            'require_reset_password',
            'has_password',
        )

    def get_nodes(self, obj):    # pylint: disable=no-self-use
        '''
        groups + nodes
        出于业务需要，extern 不予展示
        '''
        return GroupLiteSerializer([group for group in obj.groups if group.uid != 'extern'],
                                   many=True).data + DeptLiteSerializer(obj.depts, many=True).data


class SubAccountSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for sub account
    '''
    # password = serializers.CharField(write_only=True)
    uuid = serializers.UUIDField(format='hex', read_only=True)

    class Meta:    # pylint: disable=missing-docstring
        model = SubAccount

        fields = (
            'uuid',
            'domain',
            'username',
            'password',
        )


class ResetUserPasswordSerializer(DynamicFieldsModelSerializer):
    '''
    serializer for admin to reset user password
    '''
    password = serializers.CharField(required=True, write_only=True)
    require_reset_password = serializers.BooleanField(required=True)

    class Meta:    # pylint: disable=missing-docstring
        model = User

        fields = (
            'password',
            'require_reset_password',
        )

    def update(self, instance, validated_data):
        from executer.core import CLI    # pylint: disable=import-outside-toplevel
        password = validated_data.get('password')
        cli = CLI()
        cli.set_user_password(instance, password)
        instance.revoke_token()
        require_reset_password = validated_data.get('require_reset_password')
        instance.require_reset_password = require_reset_password
        instance.save(update_fields=['require_reset_password'])
        return instance

    @staticmethod
    def validate_password(value):
        """密码复杂度检验"""
        validate_password(value)
        return value

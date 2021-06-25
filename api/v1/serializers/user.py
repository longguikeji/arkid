from api.v1.serializers.permission import PermissionSerializer
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Group, Permission, User
from rest_framework import serializers
from .group import GroupSerializer, GroupBaseSerializer
from api.v1.fields.custom import (
    create_foreign_key_field, create_foreign_field, create_hint_field,
    create_mobile_field, create_password_field,
)
from ..pages import group, permission
from django.utils.translation import gettext_lazy as _


class UserSerializer(BaseDynamicFieldModelSerializer):

    groups = serializers.SerializerMethodField()
    email = create_hint_field(serializers.EmailField)(
        hint="请填写正确的email格式",
        required=False,
    )
    mobile = create_mobile_field(serializers.CharField)(
        hint="请填写正确的电话格式",
        required=False,
    )
    set_groups = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='id',
        page=group.tag,
        child=serializers.CharField(),
        write_only=True,
    )

    permissions = serializers.SerializerMethodField()

    set_permissions = create_foreign_key_field(serializers.ListField)(
        model_cls=Permission,
        field_name='id',
        page=permission.tag,
        child=serializers.CharField(),
        write_only=True,
    )

    class Meta:
        model = User

        fields = (
            'uuid',
            'username',
            'email',
            'mobile',
            'first_name',
            'last_name',
            'nickname',
            'avatar_url',
            'country',
            'city',
            'job_title',
            'groups',
            'permissions',
            'set_groups',
            'set_permissions',
            'bind_info',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
            'bind_info': {'read_only': True},
        }

    def get_groups(self, instance):
        groups = instance.groups.all()
        ret = []
        for g in groups:
            o = GroupBaseSerializer(g)
            ret.append(o.data)

        return ret

    def get_permissions(self, instance):
        user_permissions = instance.user_permissions.all()
        ret = []
        for p in user_permissions:
            o = PermissionSerializer(p)
            ret.append(o.data)
        return ret

    def create(self, validated_data):
        set_groups = validated_data.pop('set_groups', None)
        set_permissions = validated_data.pop('set_permissions', None)

        u: User = User.objects.create(
            **validated_data,
        )

        u.tenants.add(self.context['tenant'])

        if set_groups is not None:
            u.groups.clear()
            for g_uuid in set_groups:
                g = Group.objects.filter(uuid=g_uuid).first()
                if g is not None:
                    u.groups.add(g)

        if set_permissions is not None:
            u.user_permissions.clear()
            for p_uuid in set_permissions:
                p = Permission.objects.filter(uuid=p_uuid).first()
                if p is not None:
                    u.user_permissions.add(p)
        u.save()
        return u

    def update(self, instance, validated_data):
        set_groups = validated_data.pop('set_groups', None)
        set_permissions = validated_data.pop('set_permissions', None)
        if set_groups is not None:
            instance.groups.clear()
            for g_uuid in set_groups:
                g = Group.objects.filter(uuid=g_uuid).first()
                if g is not None:
                    instance.groups.add(g)

        if set_permissions is not None:
            instance.user_permissions.clear()
            for p_uuid in set_permissions:
                p = Permission.objects.filter(uuid=p_uuid).first()
                if p is not None:
                    instance.user_permissions.add(p)

        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class UserListResponsesSerializer(UserSerializer):
    class Meta:
        model = User

        fields = (
            'username',
            'email',
            'mobile',
            'first_name',
            'last_name',
            'nickname',
            'country',
            'city',
            'job_title',
            'bind_info',
        )


class TokenRequestSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('需要验证的token'))


class TokenSerializer(serializers.Serializer):

    is_valid = serializers.BooleanField(label=_('是否有效'))


class PasswordRequestSerializer(serializers.Serializer):

    uuid = serializers.CharField(label=_('用户uuid'))
    password = create_password_field(serializers.CharField)(
        label=_('新密码'),
        hint="密码长度大于等于8位的字母数字组合",
        write_only=True,
        required=False,
    )
    old_password = create_password_field(serializers.CharField)(
        label=_('旧密码'),
        hint="密码长度大于等于8位的字母数字组合",
        write_only=True,
        required=False,
    )


class ResetPasswordRequestSerializer(serializers.Serializer):

    uuid = serializers.CharField(label=_('用户uuid'))
    tenant_uuid = serializers.CharField(label=_('租户uuid'))
    password = create_password_field(serializers.CharField)(
        label=_('密码'),
        hint="密码长度大于等于8位的字母数字组合",
        write_only=True,
        required=True,
    )


class PasswordSerializer(serializers.Serializer):

    is_succeed = serializers.BooleanField(label=_('是否修改成功'))


class UserImportSerializer(serializers.Serializer):

    file = serializers.FileField(label=_('上传文件'), write_only=True)
    error = serializers.CharField(read_only=True)
    message = serializers.CharField(read_only=True)


class UserInfoSerializer(BaseDynamicFieldModelSerializer):
    uuid = serializers.CharField(label=_('uuid'), read_only=True)
    username = serializers.CharField(label=_('用户名'), read_only=True)
    nickname = serializers.CharField(label=_('昵称'), required=False, allow_blank=True)
    mobile = create_mobile_field(serializers.CharField)(
        label=_('手机号'),
        hint="请填写正确的电话格式",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = User

        fields = (
            'uuid',
            'username',
            'nickname',
            'mobile',
        )

    def update(self, instance, validated_data):
        nickname = validated_data.pop('nickname', None)
        if nickname:
            instance.nickname = nickname
        mobile = validated_data.pop('mobile', None)
        if mobile:
            instance.mobile = mobile
        instance.save()
        return instance


class UserBindInfoBaseSerializer(serializers.Serializer):
    name = serializers.CharField(label=_('名称'), read_only=True)
    tenant = serializers.CharField(label=_('租户'), read_only=True)
    unbind = serializers.CharField(label=_('解绑地址'), read_only=True)


class UserBindInfoSerializer(serializers.Serializer):
    data = serializers.ListField(child=UserBindInfoBaseSerializer(), label=_('绑定信息'), read_only=True)


class LogoutSerializer(serializers.Serializer):
    is_succeed = serializers.BooleanField(label=_('是否退出成功'))


class UserManageTenantsSerializer(serializers.Serializer):
    manage_tenants = serializers.ListField(child=serializers.CharField(), label=_('管理的租户信息'), read_only=True)
    is_global_admin = serializers.BooleanField(label=_('是否是系统管理员'))
    is_platform_user = serializers.BooleanField(label=_('是否是平台用户'))

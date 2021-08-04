from tenant.models import(
    Tenant, TenantConfig, TenantPasswordComplexity,
    TenantContactsConfig, TenantContactsUserFieldConfig,
)
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Permission, Group, User
from api.v1.fields.custom import (
    create_enum_field, create_choice_field,
    create_foreign_key_field,
)
from ..pages import group, user


class TenantSerializer(BaseDynamicFieldModelSerializer):

    class Meta:
        model = Tenant

        fields = (
            'uuid',
            'name',
            'slug',
            'icon',
            'created',
        )

    def create(self, validated_data):
        tenant = Tenant.objects.create(
            **validated_data
        )
        user = self.context['request'].user
        if user and user.username != "":
            user.tenants.add(tenant)
        permission = Permission.active_objects.filter(codename=tenant.admin_perm_code).first()
        if permission:
            user.user_permissions.add(permission)
        # 创建密码规则
        TenantPasswordComplexity.active_objects.get_or_create(
            is_apply=True,
            tenant=tenant,
            title='6-18位字母、数字、特殊字符组合',
            regular='^(?=.*[A-Za-z])(?=.*\d)(?=.*[~$@$!%*#?&])[A-Za-z\d~$@$!%*#?&]{6,18}$'
        )
        # 通讯录配置功能开关
        TenantContactsConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            config_type=0,
            data={
                "is_open": True
            }
        )
        # 通讯录配置分组可见性
        TenantContactsConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            config_type=1,
            data={
                "visible_type": '所有人可见',
                "visible_scope": [],
                "assign_group": [],
                "assign_user": []
            }
        )
        # 字段可见性
        TenantContactsUserFieldConfig.objects.get_or_create(
                is_del=False,
                tenant=tenant,
                name="用户名",
                data={
                    "visible_type": "所有人可见",
                    "visible_scope": [],
                    "assign_group": [],
                    "assign_user": []
                }
            )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="姓名",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": []
            }
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="电话",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": []
            }
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="邮箱",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": []
            }
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="职位",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": []
            }
        )
        return tenant


class TenantExtendSerializer(BaseDynamicFieldModelSerializer):

    class Meta:
        model = Tenant

        fields = (
            'uuid',
            'name',
            'slug',
            'icon',
            'created',
            'password_complexity',
        )


class MobileLoginRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'))
    code = serializers.CharField(label=_('验证码'))


class MobileLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
    has_tenant_admin_perm = serializers.ListField(child=serializers.CharField(), label=_('权限列表'))


class MobileRegisterRequestSerializer(serializers.Serializer):

    mobile = serializers.CharField(label=_('手机号'))
    code = serializers.CharField(label=_('验证码'))
    password = serializers.CharField(label=_('密码'))


class MobileRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class UserNameRegisterRequestSerializer(serializers.Serializer):

    username = serializers.CharField(label=_('用户名'))
    password = serializers.CharField(label=_('密码'))


class UserNameLoginRequestSerializer(serializers.Serializer):

    username = serializers.CharField(label=_('用户名'))
    password = serializers.CharField(label=_('密码'))
    code = serializers.CharField(label=_('图片验证码'), required=False)
    code_filename = serializers.CharField(label=_('图片验证码的文件名称'), required=False)


class UserNameRegisterResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))


class UserNameLoginResponseSerializer(serializers.Serializer):

    token = serializers.CharField(label=_('token'))
    has_tenant_admin_perm = serializers.ListField(child=serializers.CharField(), label=_('权限列表'))


class ConfigSerializer(serializers.Serializer):
    is_open_authcode = serializers.BooleanField(label=_('是否打开验证码'))
    error_number_open_authcode = serializers.IntegerField(label=_('错误几次提示输入验证码'))
    is_open_register_limit = serializers.BooleanField(label=_('是否限制注册用户'))
    register_time_limit = serializers.IntegerField(label=_('用户注册时间限制(分钟)'))
    register_count_limit = serializers.IntegerField(label=_('用户注册数量限制'))
    upload_file_format = serializers.ListField(child=serializers.CharField(), label=_('允许上传的文件格式'))
    close_page_auto_logout = serializers.BooleanField(label=_('是否关闭页面自动退出'))


class TenantConfigSerializer(BaseDynamicFieldModelSerializer):

    data = ConfigSerializer()

    class Meta:
        model = TenantConfig

        fields = (
            'data',
        )

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = data
        instance.save()
        return instance


class TenantPasswordComplexitySerializer(BaseDynamicFieldModelSerializer):
    regular = serializers.CharField(label=_('正则表达式'))
    is_apply = serializers.BooleanField(label=_('是否应用'))
    title = serializers.CharField(label=_('标题'))

    class Meta:
        model = TenantPasswordComplexity

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
        tenant_uuid = self.context['request'].parser_context.get('kwargs').get('tenant_uuid')
        regular = validated_data.get('regular')
        is_apply = validated_data.get('is_apply')
        title = validated_data.get('title')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        complexity = TenantPasswordComplexity()
        complexity.tenant = tenant
        complexity.regular = regular
        complexity.is_apply = is_apply
        complexity.title = title
        complexity.save()
        if is_apply is True:
            TenantPasswordComplexity.active_objects.filter(tenant=tenant).exclude(id=complexity.id).update(is_apply=False)
        return complexity

    def update(self, instance, validated_data):
        tenant_uuid = self.context['request'].parser_context.get('kwargs').get('tenant_uuid')
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
        is_apply = validated_data.get('is_apply')
        if is_apply is True:
            TenantPasswordComplexity.active_objects.filter(tenant=tenant).exclude(id=instance.id).update(is_apply=False)
        instance.__dict__.update(validated_data)
        instance.save()
        return instance


class FunctionSwitchSerializer(serializers.Serializer):
    is_open = serializers.BooleanField(label=_('是否打开通讯录'))


class TenantContactsConfigFunctionSwitchSerializer(BaseDynamicFieldModelSerializer):
    data = FunctionSwitchSerializer()

    class Meta:
        model = TenantContactsConfig

        fields = (
            'data',
        )


class InfoVisibilitySerializer(serializers.Serializer):
    visible_type = serializers.ChoiceField(choices=(('所有人可见', '部分人可见')), label=_('可见类型'))
    visible_scope = serializers.MultipleChoiceField(choices=(('本人可见', '管理员可见', '指定分组与人员')), label=_('可见范围'), required=False, default=[])
    assign_group = create_foreign_key_field(serializers.ListField)(
        model_cls=Group,
        field_name='uuid',
        page=group.tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的分组')
    )

    assign_user = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='uuid',
        page=user.tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的人员')
    )


class TenantContactsConfigInfoVisibilitySerializer(BaseDynamicFieldModelSerializer):

    name = serializers.CharField(read_only=True)
    data = InfoVisibilitySerializer()

    class Meta:
        model = TenantContactsUserFieldConfig

        fields = (
            'uuid',
            'data',
            'name',
        )

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = {
            'visible_type': data.get('visible_type'),
            'visible_scope': list(data.get('visible_scope')),
            'assign_group': data.get('assign_group'),
            'assign_user': data.get('assign_user'),
        }
        instance.save()
        return instance


class GroupVisibilitySerializer(serializers.Serializer):
    visible_type = serializers.ChoiceField(choices=(('所有人可见', '部分人可见')), label=_('可见类型'))
    visible_scope = serializers.MultipleChoiceField(choices=(('组内成员可见', '下属分组可见', '指定分组与人员')), label=_('可见范围'))
    assign_group = create_foreign_key_field(serializers.ListField)(
        model_cls=Group,
        field_name='uuid',
        page=group.tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的分组')
    )

    assign_user = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='uuid',
        page=user.tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的人员')
    )


class TenantContactsConfigGroupVisibilitySerializer(BaseDynamicFieldModelSerializer):
    data = GroupVisibilitySerializer()

    class Meta:
        model = TenantContactsConfig

        fields = (
            'data',
        )

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = {
            'visible_type': data.get('visible_type'),
            'visible_scope': list(data.get('visible_scope')),
            'assign_group': data.get('assign_group'),
            'assign_user': data.get('assign_user'),
        }
        instance.save()
        return instance


class ContactsGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('name', 'uuid')


class ContactsUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'nickname', 'mobile', 'email', 'job_title')


class TenantContactsUserTagsSerializer(serializers.Serializer):

    myself_field = serializers.ListField(child=serializers.CharField(), label=_('本人可见字段'), default=[])
    manager_field = serializers.ListField(child=serializers.CharField(), label=_('管理员可见字段'), default=[])
    part_field = serializers.ListField(child=serializers.CharField(), label=_('部分人可见'), default=[])
    all_user_field = serializers.ListField(child=serializers.CharField(), label=_('所有人可见字段'), default=[])


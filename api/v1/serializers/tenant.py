from rest_framework.exceptions import ValidationError
from tenant.models import (
    Tenant,
    TenantConfig,
    TenantContactsConfig,
    TenantContactsUserFieldConfig,
    TenantDesktopConfig,
    TenantLogConfig,
    TenantSwitch,
)
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from common.serializer import BaseDynamicFieldModelSerializer
from inventory.models import Permission, Group, User
from api.v1.fields.custom import (
    create_enum_field,
    create_foreign_key_field,
    create_upload_url_field,
    create_upload_img_field,
    create_html_field,
)
from ..pages import group, user
from config.models import PasswordComplexity
from arkid.settings import MENU
import uuid


class TenantSerializer(BaseDynamicFieldModelSerializer):

    icon = create_upload_url_field(serializers.URLField)(
        hint=_("请选择图标"), required=False
    )
    use_slug = serializers.BooleanField(default=True, label=_('是否使用Slug'))
    background_url = create_upload_img_field(serializers.CharField)(
        hint=_("请选择背景图片"), required=False, label=_('登录页背景图片')
    )

    class Meta:
        model = Tenant

        fields = (
            'uuid',
            'name',
            'slug',
            'icon',
            'use_slug',
            'created',
            'background_url',
            'copyright_text',
        )

    def create(self, validated_data):
        tenant = Tenant.objects.create(**validated_data)
        user = self.context['request'].user
        if user and user.username != "":
            user.tenants.add(tenant)
        permission = Permission.active_objects.filter(
            is_system_permission=True, codename=tenant.admin_perm_code
        ).first()
        if permission:
            user.user_permissions.add(permission)
        # 创建密码规则
        PasswordComplexity.active_objects.get_or_create(
            is_apply=True,
            tenant=tenant,
            title='6-18位字母、数字、特殊字符组合',
            regular='^(?=.*[A-Za-z])(?=.*\d)(?=.*[~$@$!%*#?&])[A-Za-z\d~$@$!%*#?&]{6,18}$',
        )
        # 通讯录配置功能开关
        TenantContactsConfig.objects.get_or_create(
            is_del=False, tenant=tenant, data={"is_open": True}
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
                "assign_user": [],
            },
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="姓名",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": [],
            },
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="电话",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": [],
            },
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="邮箱",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": [],
            },
        )
        TenantContactsUserFieldConfig.objects.get_or_create(
            is_del=False,
            tenant=tenant,
            name="职位",
            data={
                "visible_type": "所有人可见",
                "visible_scope": [],
                "assign_group": [],
                "assign_user": [],
            },
        )
        # 新建权限
        content_type = ContentType.objects.get_for_model(Tenant)
        items = MENU
        for item in items:
            codename = 'enter_{}'.format(uuid.uuid4())
            Permission.objects.create(
                name=item,
                content_type=content_type,
                codename=codename,
                tenant=tenant,
                app=None,
                permission_category='入口',
                is_system_permission=True,
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
            'background_url',
            'copyright_text',
        )


class TenantUserRoleSerializer(TenantSerializer):

    role = serializers.CharField(label=_("用户角色"))

    class Meta:
        model = Tenant

        fields = (
            'uuid',
            'name',
            'slug',
            'icon',
            'use_slug',
            'created',
            'role',
        )


class ConfigSerializer(serializers.Serializer):
    # is_open_authcode = serializers.BooleanField(label=_('是否打开验证码'))
    # error_number_open_authcode = serializers.IntegerField(label=_('错误几次提示输入验证码'))
    is_open_register_limit = serializers.BooleanField(
        label=_('是否限制注册用户'), default=False
    )
    register_time_limit = serializers.IntegerField(label=_('用户注册时间限制(分钟)'), default=1)
    register_count_limit = serializers.IntegerField(label=_('用户注册数量限制'), default=10)
    upload_file_format = serializers.ListField(
        child=serializers.CharField(),
        label=_('允许上传的文件格式'),
        default=['jpg', 'png', 'gif', 'jpeg'],
    )
    close_page_auto_logout = serializers.BooleanField(
        label=_('是否关闭页面自动退出'), default=False
    )
    # password_validity_period = serializers.IntegerField(label=_('密码有效期(天)'), default=60)


class TenantConfigSerializer(BaseDynamicFieldModelSerializer):

    data = ConfigSerializer()

    class Meta:
        model = TenantConfig

        fields = ('data',)

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = data
        instance.save()
        return instance


class FunctionSwitchSerializer(serializers.Serializer):
    is_open = serializers.BooleanField(label=_('是否打开通讯录'))


class TenantContactsConfigFunctionSwitchSerializer(BaseDynamicFieldModelSerializer):
    data = FunctionSwitchSerializer()

    class Meta:
        model = TenantContactsConfig

        fields = ('data',)


class InfoVisibilitySerializer(serializers.Serializer):
    visible_type = serializers.ChoiceField(
        choices=(('所有人可见', '部分人可见')), label=_('可见类型')
    )
    visible_scope = serializers.MultipleChoiceField(
        choices=(('本人可见', '管理员可见', '指定分组与人员')),
        label=_('可见范围'),
        required=False,
        default=[],
    )
    assign_group = create_foreign_key_field(serializers.ListField)(
        model_cls=Group,
        field_name='uuid',
        page=group.group_tree_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的分组'),
    )

    assign_user = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='uuid',
        page=user.user_table_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的人员'),
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

    visible_type = serializers.ChoiceField(
        choices=(('所有人可见', '部分人可见')), label=_('可见类型')
    )
    visible_scope = serializers.MultipleChoiceField(
        choices=(('组内成员可见', '下属分组可见', '指定分组与人员')), label=_('可见范围')
    )
    assign_group = create_foreign_key_field(serializers.ListField)(
        model_cls=Group,
        field_name='uuid',
        page=group.group_tree_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的分组'),
    )

    assign_user = create_foreign_key_field(serializers.ListField)(
        model_cls=User,
        field_name='uuid',
        page=user.user_table_tag,
        child=serializers.CharField(),
        required=False,
        default=[],
        label=_('指定的人员'),
    )


class TenantContactsConfigGroupVisibilitySerializer(BaseDynamicFieldModelSerializer):
    data = GroupVisibilitySerializer()

    class Meta:
        model = TenantContactsConfig

        fields = ('data',)

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

    myself_field = serializers.ListField(
        child=serializers.CharField(), label=_('本人可见字段'), default=[]
    )
    manager_field = serializers.ListField(
        child=serializers.CharField(), label=_('管理员可见字段'), default=[]
    )
    part_field = serializers.ListField(
        child=serializers.CharField(), label=_('部分人可见'), default=[]
    )
    all_user_field = serializers.ListField(
        child=serializers.CharField(), label=_('所有人可见字段'), default=[]
    )


class DesktopConfigSerializer(serializers.Serializer):
    access_with_desktop = serializers.BooleanField(label=_("用户是否能看到桌面"), required=False)
    icon_custom = serializers.BooleanField(label=_("用户是否可以自主调整桌面图标的位置"), required=False)


class TenantDesktopConfigSerializer(BaseDynamicFieldModelSerializer):
    data = DesktopConfigSerializer(label=_("设置"))

    class Meta:
        model = TenantDesktopConfig

        fields = ('data',)

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance_data = instance.data
        access_with_desktop = data.get('access_with_desktop', None)
        icon_custom = data.get('icon_custom', None)
        if access_with_desktop is not None or icon_custom is not None:
            if access_with_desktop is not None:
                instance_data['access_with_desktop'] = access_with_desktop
            if icon_custom is not None:
                instance_data['icon_custom'] = icon_custom
            instance.data = instance_data
            instance.save()
        return instance



class TenantCollectInfoSerializer(serializers.Serializer):

    app_count = serializers.IntegerField(label=_('应用数'))
    user_count = serializers.IntegerField(label=_('用户数'))
    message_count = serializers.IntegerField(label=_('消息数'))

class TenantCheckPermissionItemSerializer(serializers.Serializer):

    uuid = serializers.CharField()
    codename = serializers.CharField(label=_("codename"))
    is_system_permission = serializers.BooleanField(label=_("是否是系统权限"))
    name = serializers.CharField(label=_("权限名称"))
    permission_category = serializers.CharField(label=_("权限类型"))


class TenantCheckPermissionSerializer(serializers.Serializer):
    is_childmanager = serializers.BooleanField(label=_("是否是子管理员"))
    is_all_show = serializers.BooleanField(label=_("是否可以看到所有"))
    is_all_application = serializers.BooleanField(label=_("是否可以所有应用"))
    permissions = serializers.ListField(
        child=TenantCheckPermissionItemSerializer(), label=_('权限'), default=[]
    )


class LogConfigSerializer(serializers.Serializer):
    log_api = serializers.CharField(label=_('日志读取API'), read_only=True)
    log_retention_period = serializers.IntegerField(label=_('日志保留时间(天)'))

    # account_ids = serializers.ListField(
    #     child=serializers.CharField(), label=_('用户账号ID'), default=[])


class TenantLogConfigSerializer(BaseDynamicFieldModelSerializer):

    data = LogConfigSerializer(label=_("设置数据"))

    class Meta:
        model = TenantLogConfig

        fields = ('data',)

    def update(self, instance, validated_data):
        data = validated_data.get('data')
        instance.data = {
            'log_api': data.get('log_api'),
            'log_retention_period': data.get('log_retention_period'),
        }
        instance.save()
        return instance


class TenantSwitchSerializer(serializers.ModelSerializer):

    switch = serializers.BooleanField(label=_("租户开关"), default=True)

    class Meta:
        model = TenantSwitch
        fields = ('switch',)


class TenantSwitchInfoSerializer(serializers.Serializer):

    switch = serializers.BooleanField(label=_("租户开关"))
    platform_tenant_uuid = serializers.CharField(label=_("平台租户uuid"))

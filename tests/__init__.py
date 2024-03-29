from django.test import Client, TestCase as django_TestCase
from arkid.core.models import *
from arkid.extension.models import *
from webhook.models import *
from arkid.core.token import generate_token

import uuid
class TestCase(django_TestCase):
    '''
    base TestCase
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def setUp(self):
        # 租户
        self.tenant = Tenant.valid_objects.filter(slug='').first()
        # 用户
        self.user = User.valid_objects.filter(username='admin').first()
        # self.user.avatar = "https://img-blog.csdnimg.cn/20211011132942637.png"
        # self.user.save()
        # token
        token_obj, _ = ExpiringToken.objects.get_or_create(user=self.user, defaults={"token": generate_token()})
        if token_obj.expired(self.tenant) is True:
            token_obj.token = generate_token()
            token_obj.save()
        token = token_obj.token

        self.client = Client(HTTP_AUTHORIZATION='Token {}'.format(token))
        # 应用
        self.app = App.objects.create(
            tenant=self.tenant,
            name='预置应用',
        )
        permission = SystemPermission()
        permission.name = self.app.name
        permission.code = 'entry_{}'.format(uuid.uuid4())
        permission.tenant = self.tenant
        permission.category = 'entry'
        permission.is_system = True
        permission.save()
        self.app.entry_permission = permission
        self.app.save()
        # 生命周期
        self.account_life = TenantExtensionConfig.objects.create(
            extension=Extension.valid_objects.get(package="com.longgui.account.life.arkid"),
            tenant=self.tenant,
            name='账号生命周期',
            config=[
                {
                    "user":{
                        "id":"faf5aae6-3cdf-4595-8b4a-3a06b31117c8",
                        "username":"admin"
                    },
                    "expiration_time":"2023-09-28 15:34:00"
                }
            ],
            type="user_expiration"
        )
        # 应用分组
        self.app_group = AppGroup.objects.create(
            tenant=self.tenant,
            name='基础分组',
        )
        self.app_group.apps.add(self.app)
        # 审批动作
        self.approve_action = ApproveAction.objects.create(
            name='动作1',
            path='/api/v1/tenant/{tenant_id}/apinfo/',
            method='GET',
            extension=Extension.valid_objects.get(type='approve_system'),
            tenant=self.tenant,
        )
        # 审批系统
        self.approve_system = TenantExtensionConfig.objects.create(
            extension=Extension.valid_objects.get(package="com.longgui.approve.system.arkid"),
            tenant=self.tenant,
            name='一个审批创建',
            config={
                "pass_request_url":"",
                "deny_request_url":""
            },
            type="approve_system_arkid"
        )
        # 认证因素
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.get(package='com.longgui.auth.factor.password')
        config.config = {
            "login_enabled_field_names":[
                {
                    "key":"username"
                }
            ],
            "register_enabled_field_names":[
                {
                    "key":"username"
                }
            ],
            "is_apply":False,
            "regular":"",
            "title":""
        }
        config.name = "default"
        config.type = "password"
        config.save()
        self.auth_factor = config
        # 认证规则
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.get(package='com.longgui.authrule.retrytimes')
        config.config = {
            "main_auth_factor":{
                "id":"70f8d39e30cc40de8a70ec6495c21e84",
                "name":"default",
                "package":"com.longgui.auth.factor.password"
            },
            "try_times":3,
            "second_auth_factor":{
                "id":"7316fc337547450aa4d4038567949ec2",
                "name":"图形验证码",
                "package":"com.longgui.auth.factor.authcode"
            },
            "expired":30
        }
        config.name = '认证规则:登录失败三次启用图形验证码'
        config.type = 'retry_times'
        config.save()
        self.auth_rules = config
        # 自动认证
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.get(package='com.longgui.auto.auth.kerberos')
        config.config = {
            "service_principal":"http://localhost:8001"
        }
        config.name = 'test认证'
        config.type = 'kerberos'
        config.save()
        self.auto_auth = config
        # 一个插件
        self.extension = Extension.active_objects.order_by('-created').first()
        # 主题
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.filter(package = 'com.longgui.theme.bootswatch').first()
        config.config = {
            "priority":1,
            "css_url":"https://bootswatch.com/5/materia/bootstrap.min.css"
        }
        config.name = 'test'
        config.type = 'materia'
        config.save()
        self.front_theme = config
        # 语言
        self.language_data = LanguageData.objects.create(name='语言包')
        # 消息
        self.message = Message.objects.create(title='测试消息', sender=self.user ,user=self.user, content='消息内容', url='http://localhost:8000')
        # github
        self.github = Extension.valid_objects.filter(package='com.longgui.external.idp.github').first()
        # 一个系统权限
        self.system_permission = SystemPermission.valid_objects.filter(tenant__isnull=True).order_by('-created').first()
        # 权限分组
        self.system_permission_group = SystemPermission.valid_objects.filter(category='group').first()
        # 授权规则
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.get(package='com.longgui.impower.rule')
        config.config = {
            "matchfield":{
                "id":"mobile",
                "name":"Mobile"
            },
            "matchsymbol":"等于",
            "matchvalue":"15291584671",
            "app":{
                "id":"arkid",
                "name":"arkid"
            },
            "permissions":[
                {
                    "id":"f547ce72-a230-41f6-b3d0-4d68fcc5dff4",
                    "sort_id":9,
                    "name":"公开app列表"
                }
            ]
        }
        config.name = 'test'
        config.type = 'DefaultImpowerRule'
        config.save()
        self.permission_rule = config
        # 权限
        permission = Permission()
        permission.tenant = self.tenant
        permission.name = '自建权限'
        permission.category = 'other'
        permission.code = 'other_{}'.format(uuid.uuid4())
        permission.parent = None
        permission.app = self.app
        permission.is_system = False
        permission.save()
        self.permission = permission
        # 用户分组
        self.user_group = UserGroup.valid_objects.filter(tenant=self.tenant).first()
        # 注册配置
        self.register_config = TenantExtensionConfig.valid_objects.filter(extension__package='com.longgui.auth.factor.password', tenant=self.tenant).first()
        # 数据同步
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.get(package='com.longgui.scim.sync.arkid')
        config.config = {
            "user_url":"",
            "group_url":"",
            "mode":"server"
        }
        config.name = '一个新服务配置'
        config.type = 'ArkID'
        config.save()
        self.scim_sync = config
        # 飞书可能会没有
        self.feishu = TenantExtensionConfig.valid_objects.filter(extension__package='com.longgui.external.idp.feishu', tenant=self.tenant).first()
        # 新租户
        # only_name = uuid.uuid4().hex
        # self.create_tenant = Tenant.objects.create(name=only_name, slug=only_name, icon='')
        self.create_tenant = Tenant.valid_objects.exclude(slug='').order_by('-created').first()
        if self.create_tenant is None:
            self.create_tenant = self.tenant
        # 第三方认证
        config = TenantExtensionConfig()
        config.tenant = self.tenant
        config.extension = Extension.active_objects.get(package='com.longgui.external.idp.dingding')
        config.config = {
            "app_key":"aa",
            "app_secret":"bb",
            "img_url":"",
            "login_url":"",
            "callback_url":"",
            "bind_url":"",
            "frontend_callback":""
        }
        config.name = 'ssst'
        config.type = 'dingding'
        config.save()
        self.third_auth = config
        # 用户分组
        user_group = UserGroup.objects.create(tenant=self.tenant, name='一个新分组')
        systempermission = SystemPermission()
        systempermission.name = user_group.name
        systempermission.code = 'group_{}'.format(uuid.uuid4())
        systempermission.tenant = self.tenant
        systempermission.category = 'group'
        systempermission.is_system = True
        systempermission.operation_id = ''
        systempermission.describe = {}
        systempermission.save()
        user_group.permission = systempermission
        user_group.save()
        user_group.users.add(self.user)
        self.user_group = user_group
        # 一个新用户
        create_user = User.objects.create(username='sssss', tenant=self.tenant)
        self.create_user = create_user
        # webhook
        webhook = Webhook.objects.create(tenant=self.tenant, name='xxx', url='https://www.baidu.com', secret='xxxx')
        self.webhook = webhook
        # webhook 历史记录
        webhook_triggerhistory = WebhookTriggerHistory.objects.create(tenant=self.tenant, webhook=self.webhook, request='', response='')
        self.webhook_triggerhistory = webhook_triggerhistory
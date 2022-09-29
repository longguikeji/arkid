from django.test import Client, TestCase as django_TestCase
from arkid.core.models import *
from arkid.extension.models import *
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
        self.extension = Extension.active_objects.first()
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
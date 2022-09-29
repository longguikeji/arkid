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
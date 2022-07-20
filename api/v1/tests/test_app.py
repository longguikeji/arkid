from api.v1.tests import TestCase

class TestAppCase(TestCase):
    '''
    测试应用
    '''
    def setUp(self):
        super().setUp()

    def tearDown(self):
        pass

    def test_insert_app(self):
        from arkid.core.models import (
            App, Tenant, SystemPermission,
            TenantExtensionConfig, Extension,
        )
        import uuid
        import datetime
        tenant, _ = Tenant.objects.get_or_create(
            slug='',
            name="平台租户",
        )
        # 插入应用
        app, app_is_create = App.objects.get_or_create(
            tenant=tenant,
            name='测试应用'
        )
        print(1)
        print(datetime.datetime.now())
        tenant_id = str(tenant.id)
        permission = SystemPermission()
        permission.name = app.name
        permission.code = 'entry_{}'.format(uuid.uuid4())
        permission.tenant = tenant
        permission.category = 'entry'
        permission.is_system = True
        permission.save()
        app.entry_permission = permission
        app.save()
        app_id = str(app.id)
        print(2)
        print(datetime.datetime.now())
        from arkid.core.perm.permission_data import PermissionData
        pd = PermissionData()
        pd.update_arkid_all_user_permission(tenant_id)
        print(3)
        print(datetime.datetime.now())
        # 插入授权协议
        extension = Extension()
        extension.type = 'app_protocol'
        extension.labels = ['OAuth2', 'OIDC']
        extension.package = 'com.longgui.app.protocol.oidc'
        extension.ext_dir = 'extension_root/com_longgui_app_protocol_oidc'
        extension.name = 'OIDC&OAuth2认证协议'
        extension.version = '1.0'
        extension.profile = {}
        extension.is_allow_use_platform_config = False
        extension.save()

        config = TenantExtensionConfig()
        config.tenant = tenant
        config.extension = extension
        config.config = {
            "skip_authorization": False,
            "redirect_uris":"http://www.baidu.com",
            "client_type":"confidential",
            "grant_type":"authorization-code",
            "algorithm":"RS256",
            "client_id":"Y0nyNqIBsNBqYlW5ebGTRvgeNO6B0zZxvmFSCKWP",
            "client_secret":"LZHoJu7yZ5XnKR2dff4WlnD3BWcXTol2QBQX2IwboZUJYdVKmjvvEfRe002XK4nu1ujYZMdo3X4ow9CKiyVRLFRMoNEufhAeE0OgK5tVtRPRvVYAvKlIjE4QSaw6bRSB",
            "authorize":"http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/app/0b97eb6a-ee67-4e64-b59d-f4b49f3546ed/oauth/authorize/",
            "token":"http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/oauth/token/",
            "userinfo":"http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/oauth/userinfo/",
            "logout":"http://localhost:9528/api/v1/tenant/4da114ce-e115-44a0-823b-d372114425d0/oidc/logout/",
            "version":"1",
            "openapi_uris":"http://127.0.0.1:8000/api/v1/openapi.json"
        }
        config.save()
        app.config = config
        app.save()
        # 更新应用权限
        pd.update_app_permission(tenant_id, app_id)
        print(4)
        print(datetime.datetime.now())
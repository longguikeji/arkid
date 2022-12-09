from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.translation import gettext_default as _
from pydantic import Field
from arkid.core.event import CREATE_APP, UPDATE_APP, DELETE_APP
import os
from ninja import Query
from typing import List
from arkid.common.logger import logger
from arkid.config import get_app_config
from typing import Optional
from urllib.parse import urlparse
from arkid.core.models import ExpiringToken
from arkid.core.extension import create_extension_schema, Extension
from django.urls import reverse
from django.shortcuts import redirect
from arkid.core.models import Tenant, ExpiringToken, App, User
from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse, HttpResponse
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.config import get_app_config
from django.conf import settings
from pathlib import Path
from arkid.core.api import operation
from ninja.pagination import paginate
from arkid.core.pagenation import CustomPagination
from arkid.common.arkstore import get_app_config_from_arkstore
from .schema import *
from .error import *
from .models import AutoFormFillUser


CURRENT_DIR = Path(__file__).resolve().parent

AutoFormFillConfigSchema = create_extension_schema(
    'AutoFormFillConfigSchema',
    __file__,
    [
        ('login_url', str, Field(title=_('Auto Form Fill APP Login URL', '登录URL'))),
        (
            'username_css',
            str,
            Field(title=_('Username CSS Selector', '用户名输入框CSS Selector')),
        ),
        (
            'password_css',
            str,
            Field(title=_('Password CSS Selector', '密码输入框CSS Selector')),
        ),
        (
            'submit_css',
            str,
            Field(title=_('Submit Button CSS Selector', '提交/登录按钮CSS Selector')),
        ),
        (
            'account_type',
            Account_Type,
            Field(default='mobile_email', title=_('Account Type', '账号类型')),
        ),
        (
            'extra_js',
            str,
            Field(format="textarea", title=_('Extra Element JavaScrip Selector', '额外的元素JavaScript Selector')),
        ),
        ('auto_login', bool, Field(default=False, title=_('Auto Login', '自动登录'))),
    ],
)
AutoFormFillSettingsConfigSchema = create_extension_schema(
    'AutoFormFillSettingsConfigSchema',
    __file__,
    base_schema=AutoFormFillSettingsConfigSchema
)

class AutoFormFillExtension(AppProtocolExtension):
    def load(self):
        tmpl_dir = CURRENT_DIR / 'templates'
        settings.TEMPLATES[0]["DIRS"].append(str(tmpl_dir))
        self.register_app_protocol_schema(AutoFormFillConfigSchema, 'AutoFormFill')
        self.register_extension_api()
        self.register_pages()
        self.register_settings_schema(AutoFormFillSettingsConfigSchema)
        super().load()
    
    def register_extension_api(self):
        self.register_api('/apps/{app_id}/arkid_form_login/', 'GET', self.login, auth=None)
        self.register_api('/arkid_chrome_extension/download/', 'GET', self.download, auth=None)
        self.register_api('/apps/', 'GET', self.app_list)
        self.register_api('/apps/{app_id}/', 'GET', self.app_config)
        self.register_api('/apps/{tenant_id}/save_type/', 'GET', self.get_save_type)
        # 插件联网获取
        self.register_api('/apps/{app_id}/get_account_info/', 'GET', self.get_account_info)
        self.register_api('/apps/{app_id}/get_app_placeholder/', 'GET', self.get_app_placeholder)
        self.register_api('/apps/{tenant_id}/get_all_account/', 'GET', self.get_all_account)
        self.register_api('/apps/{app_id}/create_account/', 'POST', self.create_account)
        self.register_api('/accounts/{account_id}/get_password/', 'GET', self.get_password)
        self.register_api('/accounts/{account_id}/set_password/', 'POST', self.set_password)
        self.register_api('/accounts/{account_id}/delete/', 'DELETE', self.delete_account)
        # 账号密码增删改查(管理员)
        self.register_api('/auto_form_fill/accounts/', 'GET', self.list_auto_form_fill_accounts, response=List[AutoFormFillUserItemOut] , tenant_path=True)
        self.register_api('/auto_form_fill/accounts/', 'POST', self.create_auto_form_fill_account, tenant_path=True)
        self.register_api('/auto_form_fill/accounts/{id}/', 'GET', self.get_auto_form_fill_account, response=AutoFormFillUserOut ,tenant_path=True)
        self.register_api('/auto_form_fill/accounts/{id}/', 'PUT', self.update_auto_form_fill_account, tenant_path=True)
        self.register_api('/auto_form_fill/accounts/{id}/', 'DELETE', self.delete_auto_form_fill_account, tenant_path=True)
        # 账号密码增删改查(我的)
        self.register_api('/auto_form_fill/mine/accounts/', 'GET', self.list_auto_form_fill_mine_accounts, response=List[AutoFormFillUserMineItemOut] , tenant_path=True)
        self.register_api('/auto_form_fill/mine/accounts/', 'POST', self.create_auto_form_fill_mine_account, tenant_path=True)
        self.register_api('/auto_form_fill/mine/accounts/{id}/', 'GET', self.get_auto_form_fill_mine_account, response=AutoFormFillUserMineOut ,tenant_path=True)
        self.register_api('/auto_form_fill/mine/accounts/{id}/', 'PUT', self.update_auto_form_fill_mine_account, tenant_path=True)
        self.register_api('/auto_form_fill/mine/accounts/{id}/', 'DELETE', self.delete_auto_form_fill_mine_account, tenant_path=True)

    def register_pages(self):
        from .pages import page as auto_form_fill_page
        from .pages import mine_page as auto_form_fill_mine_page
        from api.v1.pages.user_manage import router
        from api.v1.pages.mine.auth_manage import page as auth_page

        self.register_front_pages([
            auto_form_fill_page.auto_form_fill_account_page,
        ])

        self.register_front_routers(auto_form_fill_page.router, router)
        # 需要增加一个页面
        auth_page.add_pages([auto_form_fill_mine_page.auto_form_fill_account_page])
        # auth_router.children.append(auto_form_fill_mine_page.router)


    @operation(AutoFormFillUserListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def list_auto_form_fill_accounts(self, request, tenant_id:str, query_data: AutoFormFillUserQueryIn=Query(...)):
        '''
        账密代填账号列表
        '''
        username = query_data.username
        autoformfill_users = AutoFormFillUser.valid_objects.filter(tenant_id=tenant_id)
        if username:
            autoformfill_users = autoformfill_users.filter(username__icontains=username.strip())
        autoformfill_users = autoformfill_users.order_by('created')
        return autoformfill_users

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def create_auto_form_fill_account(self, request, tenant_id:str, data:AutoFormFillUserIn):
        '''
        创建账密代填账号
        '''
        username = data.username
        password = data.password
        tenant = request.tenant
        app_id = data.app.id
        user_id = data.user.id

        app = App.valid_objects.filter(
            id=app_id
        ).first()
        app_config = app.config
        if app.arkstore_app_id:
            app_config = get_app_config_from_arkstore(request, app.arkstore_app_id)
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', 'mobile_email')
            else:
                account_type = app_config.config.get('account_type', 'mobile_email')
            if self.check_username(account_type, username) is False:
                return self.error(ErrorCode.USERNAME_FORMAT_ERROR)

        if AutoFormFillUser.valid_objects.filter(
            tenant=tenant,
            user_id=user_id,
            app_id=app_id,
            username=username.strip()
        ).exists():
            return self.error(ErrorCode.USERNAME_EXISTS)
        else:
            autoformfill_user = AutoFormFillUser()
            autoformfill_user.tenant = tenant
            autoformfill_user.user_id = user_id
            autoformfill_user.app_id = app_id
            autoformfill_user.username = username.strip()
            autoformfill_user.password = self.encrypt_password(user_id, password)
            autoformfill_user.save()
            return self.success()

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def get_auto_form_fill_account(self, request, tenant_id:str, id:str):
        '''
        获取账密代填账号
        '''
        autoformfill_user = AutoFormFillUser.valid_objects.filter(
            tenant_id=tenant_id,
            id=id
        ).first()
        return self.success(data=autoformfill_user)

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def update_auto_form_fill_account(self, request, tenant_id:str, id:str, data:AutoFormFillUserIn):
        '''
        修改账密代填账号
        '''
        autoformfill_user = AutoFormFillUser.valid_objects.filter(
            tenant_id=tenant_id,
            id=id
        ).first()
        username = data.username
        password = data.password

        app_id = data.app.id
        user_id = data.user.id

        app_config = autoformfill_user.app.config
        if autoformfill_user.app.arkstore_app_id:
            app_config = get_app_config_from_arkstore(request, autoformfill_user.app.arkstore_app_id)
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', 'mobile_email')
            else:
                account_type = app_config.config.get('account_type', 'mobile_email')
            if self.check_username(account_type, username) is False:
                return self.error(ErrorCode.USERNAME_FORMAT_ERROR)

        autoformfill_user.user_id = user_id
        autoformfill_user.app_id = app_id
        autoformfill_user.username = username.strip()
        if password:
            autoformfill_user.password = self.encrypt_password(user_id, password)
        autoformfill_user.save()
        return self.success()

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def delete_auto_form_fill_account(self, request, tenant_id:str, id:str):
        '''
        删除账密代填账号
        '''
        autoformfill_user = AutoFormFillUser.valid_objects.filter(
            tenant_id=tenant_id,
            id=id
        ).first()
        autoformfill_user.delete()
        return self.success()
    
    @operation(AutoFormFillUserMineListOut, roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def list_auto_form_fill_mine_accounts(self, request, tenant_id:str, query_data: AutoFormFillUserQueryIn=Query(...)):
        '''
        账密代填账号列表(我的)
        '''
        username = query_data.username
        autoformfill_users = AutoFormFillUser.valid_objects.filter(tenant_id=tenant_id, user=request.user)
        if username:
            autoformfill_users = autoformfill_users.filter(username__icontains=username.strip())
        autoformfill_users = autoformfill_users.order_by('created')
        return autoformfill_users

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def create_auto_form_fill_mine_account(self, request, tenant_id:str, data:AutoFormFillUserMineIn):
        '''
        创建账密代填账号(我的)
        '''
        username = data.username
        password = data.password
        tenant = request.tenant
        app_id = data.app.id
        user_id = request.user.id

        app = App.valid_objects.filter(
            id=app_id
        ).first()
        app_config = app.config
        if app.arkstore_app_id:
            app_config = get_app_config_from_arkstore(request, app.arkstore_app_id)
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', 'mobile_email')
            else:
                account_type = app_config.config.get('account_type', 'mobile_email')
            if self.check_username(account_type, username) is False:
                return self.error(ErrorCode.USERNAME_FORMAT_ERROR)

        if AutoFormFillUser.valid_objects.filter(
            tenant=tenant,
            user_id=user_id,
            app_id=app_id,
            username=username.strip()
        ).exists():
            return self.error(ErrorCode.USERNAME_EXISTS)
        else:
            autoformfill_user = AutoFormFillUser()
            autoformfill_user.tenant = tenant
            autoformfill_user.user_id = user_id
            autoformfill_user.app_id = app_id
            autoformfill_user.username = username.strip()
            autoformfill_user.password = self.encrypt_password(user_id, password)
            autoformfill_user.save()
            return self.success()

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def get_auto_form_fill_mine_account(self, request, tenant_id:str, id:str):
        '''
        获取账密代填账号(我的)
        '''
        autoformfill_user = AutoFormFillUser.valid_objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            id=id
        ).first()
        return self.success(data=autoformfill_user)

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def update_auto_form_fill_mine_account(self, request, tenant_id:str, id:str, data:AutoFormFillUserMineIn):
        '''
        修改账密代填账号(我的)
        '''
        autoformfill_user = AutoFormFillUser.valid_objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            id=id
        ).first()
        username = data.username
        password = data.password

        app_id = data.app.id

        app_config = autoformfill_user.app.config
        if autoformfill_user.app.arkstore_app_id:
            app_config = get_app_config_from_arkstore(request, autoformfill_user.app.arkstore_app_id)
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', 'mobile_email')
            else:
                account_type = app_config.config.get('account_type', 'mobile_email')
            if self.check_username(account_type, username) is False:
                return self.error(ErrorCode.USERNAME_FORMAT_ERROR)

        # autoformfill_user.user_id = user_id
        autoformfill_user.app_id = app_id
        autoformfill_user.username = username.strip()
        if password:
            user_id = request.user.id
            autoformfill_user.password = self.encrypt_password(user_id, password)
        autoformfill_user.save()
        return self.success()

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def delete_auto_form_fill_mine_account(self, request, tenant_id:str, id:str):
        '''
        删除账密代填账号(我的)
        '''
        autoformfill_user = AutoFormFillUser.valid_objects.filter(
            user=request.user,
            tenant_id=tenant_id,
            id=id
        ).first()
        autoformfill_user.delete()
        return self.success()

    def encrypt_password(self, user_id, password):
        '''
        对密码进行加密
        '''
        import cryptocode
        key = user_id.hex
        return cryptocode.encrypt(password, key)
    
    def decrypt_password(self, user_id, password):
        '''
        对密码进行解密
        '''
        import cryptocode
        key = user_id.hex
        return cryptocode.decrypt(password, key)

    def create_app(self, event, **kwargs):
        self.update_app_url(event, True)
        return True

    def update_app(self, event, **kwargs):
        self.update_app_url(event, False)
        return True

    def delete_app(self, event, **kwargs):
        # 删除应用
        return True

    def update_app_url(self, event, is_created):
        '''
        更新配置中的url信息
        '''
        app = event.data["app"]
        config = get_app_config()
        frontend_url = config.get_frontend_host(schema=True)

        app.url = (
            f'{frontend_url}/api/v1/{self.pname}/apps/{app.id.hex}/arkid_form_login/'
        )
        app.save()

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def login(self, request, app_id, tenant_id=None):
        """
        判断是否已经授权过，如果没有跳转到输入账号表单页面,发起认证授权
        如果已经授权过，直接拿到已经保存的token，获取authkey，登录易签宝官网首页
        """
        token = request.GET.get("token")
        if not token:
            login_url = reverse('login_enter')
            if tenant_id:
                response = redirect(
                    f'{login_url}?next=/api/v1/{self.pname}/apps/{app_id}/arkid_form_login/&tenant_id={tenant_id}'
                )
            else:
                response = redirect(
                    f'{login_url}?next=/api/v1/{self.pname}/apps/{app_id}/arkid_form_login/'
                )
            return response

        errors = []

        app = App.valid_objects.get(id=app_id)
        expiring_token = ExpiringToken.objects.get(token=token)

        user = expiring_token.user
        tenant = user.tenant

        if app.tenant != tenant:
            errors.append("错误的app_uuid,找不到该自动表单代填应用")

        err_msg = "|".join(errors)

        config = get_app_config()
        frontend_url = config.get_frontend_host(schema=True)
        tenant_extension = self.model.tenantextension_set.filter(tenant_id=app.tenant.id).first()
        download_url = (
            f'{frontend_url}/api/v1/{self.pname}/arkid_chrome_extension/download/'
        )
        save_type = 'web'
        if tenant_extension:
            save_type = tenant_extension.settings.get('save_type', 'web')

        app_config = app.config
        if app.arkstore_app_id:
            print('+++username:'+user.username)
            print('+++token:'+str(user.auth_token))
            request.user = user
            app_config = get_app_config_from_arkstore(request, app.arkstore_app_id)
        placeholder = ''
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', 'mobile_email')
            else:
                account_type = app_config.config.get('account_type', 'mobile_email')
            if account_type == 'mobile_email':
                placeholder = '请输入电话或邮箱'
            elif account_type == 'mobile':
                placeholder = '请输入电话'
            elif account_type == 'email':
                placeholder = '请输入邮箱'
            else:
                placeholder = '请输入账户'
        else:
            placeholder = '请输入账户'
        context = {
            "err_msg": err_msg,
            "app_uuid": app.id.hex,
            "tenant_uuid": tenant.id.hex,
            "user_uuid": user.id.hex,
            "download_url": download_url,
            "save_type": save_type,
            "placeholder": placeholder,
        }
        return render(request, "form_login.html", context=context)
    
    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def get_save_type(self, request, tenant_id):
        '''
        获取存储类型(chrome插件用)
        '''
        tenant_extension = self.model.tenantextension_set.filter(tenant_id=tenant_id).first()
        save_type = 'web'
        if tenant_extension:
            save_type = tenant_extension.settings.get('save_type', 'web')
        return {"data": save_type}


    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def download(self, request):
        """
        提供chrome 表单代填插件
        """
        file_name = "arkid_chrome_extension.zip"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, file_name)

        def file_iterator(file_path, chunk_size=512):
            """
            文件生成器,防止文件过大，导致内存溢出
            :param file_path: 文件绝对路径
            :param chunk_size: 块大小
            :return: 生成器
            """
            with open(file_path, mode="rb") as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        try:
            # 设置响应头
            # StreamingHttpResponse将文件内容进行流式传输，数据量大可以用这个方法
            response = StreamingHttpResponse(file_iterator(file_path))
            # 以流的形式下载文件,这样可以实现任意格式的文件下载
            response["Content-Type"] = "application/octet-stream"
            # Content-Disposition就是当用户想把请求所得的内容存为一个文件的时候提供一个默认的文件名
            response["Content-Disposition"] = 'attachment;filename="{}"'.format(
                file_name
            )
        except:
            return HttpResponse("Sorry but Not Found the File")
        return response

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def get_account_info(self, request, app_id,  query_data: AutoFormFillUserQueryIn=Query(...)):
        """
        返回账户的信息(chrome插件用)
        """
        user = request.user
        app = App.valid_objects.get(id=app_id)
        if not app:
            return JsonResponse({})
        autoform_fills = AutoFormFillUser.valid_objects.filter(
            app=app,
            tenant=app.tenant,
            user=request.user
        )
        if query_data.username:
            autoform_fills = autoform_fills
        items = []
        for autoform_fill in autoform_fills:
            username = autoform_fill.username
            password = autoform_fill.password
            password = self.decrypt_password(user.id, password)
            items.append({
                'id': autoform_fill.id.hex,
                'username': username
            })
        return {"data": items}

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def get_app_placeholder(self, request, app_id):
        """
        返回应用输入类型提示(chrome插件用)
        """
        app = App.valid_objects.get(id=app_id)
        if not app:
            return self.error(ErrorCode.NOT_EXITST_APP)
        app_config = app.config
        if app.arkstore_app_id:
            app_config = get_app_config_from_arkstore(request, app.arkstore_app_id)
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', '')
            else:
                account_type = app_config.config.get('account_type', '')
            if account_type == 'mobile_email':
                return self.success(data={'placeholder': _('please input mobile or email', '请输入电话或邮箱')})
            elif account_type == 'mobile':
                return self.success(data={'placeholder': _('please input mobile', '请输入电话')})
            elif account_type == 'email':
                return self.success(data={'placeholder': _('please input email', '请输入邮箱')})
        return self.success(data={'placeholder': _('please input account', '请输入账户')})


    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def get_all_account(self, request, tenant_id,  query_data: AutoFormFillUserQueryIn=Query(...)):
        """
        返回所有应用的账户信息(chrome插件用)
        """
        user = request.user
        autoform_fills = AutoFormFillUser.valid_objects.filter(
            tenant_id=tenant_id,
            user=request.user
        )
        if query_data.username:
            autoform_fills = autoform_fills
        items = []
        for autoform_fill in autoform_fills:
            username = autoform_fill.username
            password = autoform_fill.password
            password = self.decrypt_password(user.id, password)
            items.append({
                'id': autoform_fill.id.hex,
                'username': username,
                'tenant_uuid': tenant_id,
                'password': '',
                'app_uuid': autoform_fill.app.id.hex
            })
        return {"data": items}
    
    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def get_password(self, request, account_id):
        '''
        获取登录账户的密码(chrome插件用)
        '''
        user = request.user
        autoform_fill = AutoFormFillUser.valid_objects.filter(
            id=account_id,
            user=user
        ).first()
        password = ""
        if autoform_fill:
            password = autoform_fill.password
            password = self.decrypt_password(user.id, password)
        return {"data": password}

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def set_password(self, request, account_id, data:AutoFormFillUserUpdateIn):
        '''
        设置登录账户的密码(chrome插件用)
        '''
        autoform_fill = AutoFormFillUser.valid_objects.filter(
            id=account_id,
            user=request.user
        ).first()
        if autoform_fill:
            autoform_fill.password = self.encrypt_password(request.user.id, data.password)
            autoform_fill.save()
        return self.success()

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def delete_account(self, request, account_id):
        '''
        删除账户(chrome插件用)
        '''
        autoform_fill = AutoFormFillUser.valid_objects.filter(
            id=account_id,
            user=request.user
        ).first()
        if autoform_fill:
            autoform_fill.delete()
        return self.success()

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def create_account(self, request, app_id, data:AutoFormFillUserApiIn):
        '''
        创建账户
        '''
        username = data.username
        password = data.password
        user = request.user
        app = App.valid_objects.get(id=app_id)
        tenant = app.tenant
        if not app:
            return self.error(ErrorCode.NOT_EXITST_APP)

        app_config = app.config
        if app.arkstore_app_id:
            app_config = get_app_config_from_arkstore(request, app.arkstore_app_id)
        if app_config:
            if app.arkstore_app_id:
                account_type = app_config.get('account_type', 'mobile_email')
            else:
                account_type = app_config.config.get('account_type', 'mobile_email')
            if self.check_username(account_type, username) is False:
                return self.error(ErrorCode.USERNAME_FORMAT_ERROR)

        if AutoFormFillUser.valid_objects.filter(
            tenant=tenant,
            user=user,
            app=app,
            username=username.strip()
        ).exists():
            return self.error(ErrorCode.USERNAME_EXISTS)
        else:
            autoformfill_user = AutoFormFillUser()
            autoformfill_user.tenant = tenant
            autoformfill_user.user = user
            autoformfill_user.app = app
            autoformfill_user.username = username.strip()
            autoformfill_user.password = self.encrypt_password(user.id, password)
            autoformfill_user.save()
            return self.success(data={'username': username, 'id':autoformfill_user.id.hex})


    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def app_config(self, request, app_id):
        """
        返回app的config
        """
        app = App.valid_objects.get(id=app_id)
        if not app:
            return JsonResponse({})

        if app.arkstore_app_id:
            config = get_app_config_from_arkstore(request, app.arkstore_app_id)
            return config

        if app.config:
            return app.config.config
        else:
            return JsonResponse({})

    @operation(roles=[NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN])
    def app_list(self, request):
        """
        返回app的config
        """
        user = request.user
        tenant = user.tenant
        all_apps = App.valid_objects.filter(tenant=tenant, type="AutoFormFill")
        if not all_apps:
            return JsonResponse({'result': []})
        for app in all_apps:
            app_config = app.config
            if app.arkstore_app_id:
                app_config = get_app_config_from_arkstore(request, app.arkstore_app_id)
            placeholder = ''
            if app_config:
                if app.arkstore_app_id:
                    account_type = app_config.get('account_type', '')
                else:
                    account_type = app_config.config.get('account_type', '')
                if account_type == 'mobile_email':
                    placeholder = '请输入电话或邮箱'
                elif account_type == 'mobile':
                    placeholder = '请输入电话'
                elif account_type == 'email':
                    placeholder = '请输入邮箱'
                else:
                    placeholder = '请输入账户'
            else:
                placeholder = '请输入账户'
            app.placeholder = placeholder
        result = [{'uuid': app.id.hex, 'name': app.name, 'placeholder': app.placeholder} for app in all_apps]
        return JsonResponse({'result': result})

    def check_username(self, account_type, username):
        import re
        mobile_reg = "1[34578]\d{9}"
        email_reg = "\w+@[a-z0-9]+\.[a-z]+"
        username = username.strip()
        if not username:
            return False
        if account_type == 'mobile_email':
            mobile_ret = re.match(mobile_reg, username)
            if mobile_ret and len(username)==11:
                return True
            else:
                email_ret = re.match(email_reg, username)
                if email_ret:
                    return True
                else:
                    return False
        elif account_type == 'mobile':
            mobile_ret = re.match(mobile_reg, username)
            if mobile_ret and len(username)==11:
                return True
            else:
                return False
        elif account_type == 'email':
            email_ret = re.match(email_reg, username)
            if email_ret:
                return True
            else:
                return False
        elif account_type == 'no limit':
            return True
        else:
            return True


extension = AutoFormFillExtension()

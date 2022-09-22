from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.translation import gettext_default as _
from pydantic import Field
from arkid.core.event import CREATE_APP, UPDATE_APP, DELETE_APP
import os
from arkid.common.logger import logger
from arkid.config import get_app_config
from typing import Optional
from urllib.parse import urlparse
from arkid.core.models import ExpiringToken
from arkid.core.extension import create_extension_schema, Extension
from django.urls import reverse
from django.shortcuts import redirect
from arkid.core.models import Tenant, ExpiringToken, App
from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.http.response import HttpResponseRedirect, JsonResponse, HttpResponse
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.config import get_app_config
from django.conf import settings
from pathlib import Path
from arkid.common.arkstore import get_app_config_from_arkstore


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
        ('auto_login', bool, Field(default=False, title=_('Auto Login', '自动登录'))),
    ],
)


class AutoFormFillExtension(AppProtocolExtension):
    def load(self):
        tmpl_dir = CURRENT_DIR / 'templates'
        settings.TEMPLATES[0]["DIRS"].append(str(tmpl_dir))
        self.register_app_protocol_schema(AutoFormFillConfigSchema, 'AutoFormFill')
        self.register_api(
            '/apps/{app_id}/arkid_form_login/', 'GET', self.login, auth=None
        )
        self.register_api(
            '/arkid_chrome_extension/download/', 'GET', self.download, auth=None
        )
        self.register_api('/apps/', 'GET', self.app_list)
        self.register_api('/apps/{app_id}/', 'GET', self.app_config)
        super().load()

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

        download_url = (
            f'{frontend_url}/api/v1/{self.pname}/arkid_chrome_extension/download/'
        )
        context = {
            "err_msg": err_msg,
            "app_uuid": app.id.hex,
            "tenant_uuid": tenant.id.hex,
            "user_uuid": user.id.hex,
            "download_url": download_url,
        }
        return render(request, "form_login.html", context=context)

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

        result = [{'uuid': app.id.hex, 'name': app.name} for app in all_apps]
        return JsonResponse({'result': result})


extension = AutoFormFillExtension()

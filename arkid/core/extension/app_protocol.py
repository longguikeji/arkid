from django.views import View
from abc import abstractmethod
from django.urls import re_path
from arkid.core.models import App
from arkid.settings import LOGIN_URL
from django.http import HttpResponseRedirect
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import api as core_api, event as core_event

import urllib.parse

class AppProtocolExtension(Extension):
    
    TYPE = "app_protocol"
    
    
    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'app_type'
    composite_model = App
    
    @property
    def type(self):
        return AppProtocolExtension.TYPE
    
    
    def load(self):
        super().load()
        self.listen_event(core_event.CREATE_APP, self.create_app)
        self.listen_event(core_event.UPDATE_APP, self.update_app)
        self.listen_event(core_event.DELETE_APP, self.delete_app)

    def register_app_protocol_schema(self, schema, app_type):
        self.register_config_schema(schema, self.package + '_' + app_type)
        self.register_composite_config_schema(schema, app_type, exclude=['secret'])

    @abstractmethod
    def create_app(self, event, **kwargs):
        pass

    @abstractmethod
    def update_app(self, event, **kwargs):
        pass

    @abstractmethod
    def delete_app(self, event, **kwargs):
        pass
    
    def register_enter_view(self, view:View, path:str, url_name:str, type:list, tenant_urls: bool=True):
        '''
        注册统一的入口函数，方便检测
        :param view:目标View的as_view()，例如:AuthorizationView.as_view()
        :param path:需要跳转的路径，例如:r"app/(?P<app_id>[\w-]+)/oauth/authorize/$"
        :param url_name:注册的路径名称, 例如:authorize
        :param type:list:一个当前插件的类型list, 例如:['OIDC', 'OAuth2']
        :param tenant_urls: bool=True, 是否注册为租户url
        :return: 函数执行结果
        '''
        # 入口函数
        class EnterView(View):

            def get(self, request, **kwargs):
                from arkid.core.perm.permission_data import PermissionData
                permissiondata = PermissionData()
                result, alert = permissiondata.check_app_entry_permission(request, type, kwargs)
                if result:
                    return view(request)
                else:
                    return HttpResponseRedirect(self.get_login_url(request, alert))

            def get_login_url(self, request, alert):
                from arkid.config import get_app_config
                full_path = request.get_full_path()
                next_uri = urllib.parse.quote(full_path)
                host = get_app_config().get_frontend_host()
                tenant = request.tenant
                if tenant and tenant.slug:
                    redirect_url = '{}{}?alert={}&next={}'.format(get_app_config().get_slug_frontend_host(tenant.slug), LOGIN_URL, alert, next_uri)
                else:
                    redirect_url = '{}{}?tenant={}&alert={}&next={}'.format(alert, get_app_config().get_frontend_host(), LOGIN_URL, tenant.id, alert, next_uri)

            def post(self, request, **kwargs):
                from arkid.core.perm.permission_data import PermissionData
                permissiondata = PermissionData()
                result, alert = permissiondata.check_app_entry_permission(request, type, kwargs)
                if result:
                    return view(request)
                else:
                    return HttpResponseRedirect(self.get_login_url(request, alert))

        # 获取进入的路由
        entry_url = [re_path(path, EnterView.as_view(), name=url_name)]
        # 注册入口路由
        self.register_routers(entry_url, tenant_urls)

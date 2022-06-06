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
        self.listen_event(core_event.CREATE_APP_CONFIG, self.create_app)
        self.listen_event(core_event.UPDATE_APP_CONFIG, self.update_app)
        self.listen_event(core_event.DELETE_APP, self.delete_app)

    def register_app_protocol_schema(self, schema, app_type):
        """
        注册应用的schema
        Params:
            schema: schema
            app_type: 应用类型
        """
        self.register_config_schema(schema, self.package + '_' + app_type)
        self.register_composite_config_schema(schema, app_type, exclude=['secret'])

    @abstractmethod
    def create_app(self, event, **kwargs):
        """
        抽象方法，创建应用
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            bool: 是否成功执行
        """
        pass

    @abstractmethod
    def update_app(self, event, **kwargs):
        """
        抽象方法，修改应用
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            bool: 是否成功执行
        """
        pass

    @abstractmethod
    def delete_app(self, event, **kwargs):
        """
        抽象方法，删除应用
        Params:
            event: 事件参数
            kwargs: 其它方法参数
        Return:
            bool: 是否成功执行
        """
        pass
    
    def register_enter_view(self, view:View, path:str, url_name:str, type:list, tenant_urls: bool=True):
        '''
        注册统一的入口函数，方便检测
        Params:
            view: str 目标View的as_view()，例如:AuthorizationView.as_view()
            path: str 需要跳转的路径，例如:r"app/(?P<app_id>[\w-]+)/oauth/authorize/$
            url_name: str 注册的路径名称, 例如:authorize
            type: list 一个当前插件的类型list, 例如:['OIDC', 'OAuth2']
            tenant_urls: bool 是否注册为租户url
        Return:
            response: 函数执行结果
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
                    url = self.get_login_url(request, alert)
                    return HttpResponseRedirect(url)

            def get_login_url(self, request, alert):
                from arkid.config import get_app_config
                full_path = request.get_full_path()
                next_uri = urllib.parse.quote(full_path)
                host = get_app_config().get_frontend_host()
                tenant = request.tenant
                if not tenant:
                    return f'{host}{LOGIN_URL}?tenant_id=&next={next_uri}'

                token = request.GET.get('token', '')
                if not token:
                    if tenant.slug:
                        host =get_app_config().get_slug_frontend_host(tenant.slug)
                        return f'{host}{LOGIN_URL}?&next={next_uri}'
                    else:
                        return f'{host}{LOGIN_URL}?tenant_id={tenant.id}&next={next_uri}'
                
                if tenant.slug:
                    host =get_app_config().get_slug_frontend_host(tenant.slug)
                    return f'{host}{LOGIN_URL}?alert={alert}&next={next_uri}'
                else:
                    return f'{host}{LOGIN_URL}?tenant_id={tenant.id}&alert={alert}&next={next_uri}'

            def post(self, request, **kwargs):
                from arkid.core.perm.permission_data import PermissionData
                permissiondata = PermissionData()
                result, alert = permissiondata.check_app_entry_permission(request, type, kwargs)
                if result:
                    return view(request)
                else:
                    url = self.get_login_url(request, alert)
                    return HttpResponseRedirect(url)

        # 获取进入的路由
        entry_url = [re_path(path, EnterView.as_view(), name=url_name)]
        # 注册入口路由
        self.register_routers(entry_url, tenant_urls)

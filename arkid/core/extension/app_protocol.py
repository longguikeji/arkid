from django.views import View
from abc import abstractmethod
from arkid.core.models import App
from django.urls import re_path
from django.http import HttpResponse
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import api as core_api, event as core_event

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
    
    def register_enter_view(self, view:View, path:str, url_name:str, type:list):
        '''
        注册统一的入口函数，方便检测
        :param view:目标View的as_view()，例如:AuthorizationView.as_view()
        :param path:需要跳转的路径，例如:r"oauth/authorize/$"
        :param url_name:注册的路径名称, 例如:authorize
        :param type:list:一个当前插件的类型list, 例如:['OIDC', 'OAuth2']
        :return: 函数执行结果
        '''
        # 入口函数
        class EnterView(View):

            def get(self, request, **kwargs):
                from arkid.core.perm.permission_data import PermissionData
                permissiondata = PermissionData()
                result = permissiondata.check_app_entry_permission(request, type, kwargs)
                if result:
                    return view(request)
                else:
                    return HttpResponse('Unauthorized', status=401)

        # 获取进入的路由
        entry_url = [re_path(path, EnterView.as_view(), name=url_name)]
        # 注册入口路由
        self.register_routers(entry_url, True)

from typing import List
from arkid.core import actions, pages
from arkid.core.api import GlobalAuth, operation
from arkid.core.extension import Extension
from arkid.core.models import App
from arkid.core.pagenation import CustomPagination
from arkid.extension.models import TenantExtensionConfig
from arkid.core.constants import *
from .models import AppSubscribeRecord
from ninja.pagination import paginate
from .schema import *

class AppSubscribeExtension(Extension):
    
    TYPE = "other"
    
    @property
    def type(self):
        return AppSubscribeExtension.TYPE
    
    def load(self):
        self.create_mine_manage_page()
        self.listen_event(
            'api_v1_views_mine_get_mine_apps',
            self.update_mine_apps
        )
        super().load()
        
    def update_mine_apps(self,event, *args, **kwargs):
        
        user = event.request.user
        
        subscribed_apps = [ record.app.id.hex for record in AppSubscribeRecord.objects.filter(user=user).all()]
        
        data = []
        for item in event.response["data"]:
            if item.id.hex in subscribed_apps:
                data.append(item)
                
        event.response["data"] = data
        
    @operation(List[GetAllAppsItemOut],roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    @paginate(CustomPagination)
    def get_all_apps(self,request,tenant_id):
        """获取租户下所有的应用
        """
        user = request.user
        tenant = request.tenant
        apps = App.active_objects.filter(tenant=tenant).all()
        subscribed_apps = [ record.app.id.hex for record in AppSubscribeRecord.objects.filter(user=user).all()]
        return [
            {
                "id": app.id.hex,
                "name": app.name,
                "logo":app.logo,
                "is_subscribed": app.id.hex in subscribed_apps 
            } for app in apps
        ]

    @operation(ResponseSchema,roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def change_subscribe_status(self,request,tenant_id,id:str):
        """更改订阅状态
        """
        app = App.active_objects.get(id=id)
        record,is_created = AppSubscribeRecord.objects.get_or_create(app=app,user=request.user)
        
        if not is_created:
            record.delete()
        
        return self.success()

    def create_mine_manage_page(self):
        from api.v1.pages.mine.profile import page as profile_page
        
        get_all_apps_path = self.register_api(
            "/get_all_apps_path/",
            'GET',
            self.get_all_apps,
            tenant_path=True,
            auth=GlobalAuth(),
            response=List[GetAllAppsItemOut]
        )
        
        change_subscribe_status_path = self.register_api(
            "/app/{id}/change_subscribe_status/",
            "POST",
             self.change_subscribe_status,
            tenant_path=True,
            auth=GlobalAuth(),
            response=ResponseSchema
        )
        
        page = pages.CardsPage(name="应用订阅管理")
        
        page.create_actions(
            init_action=actions.DirectAction(
                path=get_all_apps_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=change_subscribe_status_path
                ),
            }
        )
        
        self.register_front_pages(page)
        profile_page.add_pages(page)

extension = AppSubscribeExtension()


import json
import re
from typing import List
from typing_extensions import Self

from django.conf import settings
from ninja import Query
import requests
from arkid.config import get_app_config
from arkid.core.api import GlobalAuth, operation
from arkid.core.error import ErrorDict, SuccessDict
from arkid.core.event import Event, dispatch_event
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.models import User, UserGroup
from arkid.core.pagenation import CustomPagination
from arkid.core.token import refresh_token
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.constants import *
from arkid.core import pages, actions, routers
from arkid.core.translation import gettext_default as _
from ninja.pagination import paginate
from .schema import *
from .error import *
from .models import *


class MultipleAccountExtension(AppProtocolExtension):

    def load(self):
        # 加载相应的配置文件
        self.register_extension_api()
        self.create_extension_settings_schema()
        self.register_pages()
        super().load()

    def create_app(self, event, **kwargs):
        pass

    def update_app(self, event, **kwargs):
        pass

    def delete_app(self, event, **kwargs):
        pass

    def create_extension_settings_schema(self):
        """ 创建插件配置schema描述
        """
        pass

    def register_extension_api(self):
        """注册插件API
        """
        self.add_multiaccount_setting_path = self.register_api(
            '/add_multiaccount_setting/',
            'POST',
            self.add_multiaccount_setting,
            tenant_path=True,
            auth=GlobalAuth(),
            response=AppMultiAccountSettingOutSchema,
        )

        self.list_multiaccount_settings_path = self.register_api(
            '/list_multiaccount_settings/',
            'GET',
            self.list_multiaccount_settings,
            tenant_path=True,
            auth=GlobalAuth(),
            response=List[AppMultiAccountSettingListItemOutSchema],
        )

        self.get_multiaccount_setting_path = self.register_api(
            '/get_multiaccount_setting/{id}/',
            'GET',
            self.get_multiaccount_setting,
            tenant_path=True,
            auth=GlobalAuth(),
            response=AppMultiAccountSettingDetailOutSchema,
        )

        self.update_multiaccount_setting_path = self.register_api(
            '/update_multiaccount_setting/{id}/',
            'POST',
            self.update_multiaccount_setting,
            tenant_path=True,
            auth=GlobalAuth(),
            response=AppMultiAccountSettingOutSchema,
        )

        self.delete_multiaccount_setting_path = self.register_api(
            '/delete_multiaccount_setting/{id}/',
            'DELETE',
            self.delete_multiaccount_setting,
            tenant_path=True,
            auth=GlobalAuth(),
            response=AppMultiAccountSettingOutSchema,
        )

        self.list_unsetting_app_path = self.register_api(
            '/unsetting_app_list/',
            'GET',
            self.unsetting_app_list,
            tenant_path=True,
            auth=GlobalAuth(),
            response=List[AppListItemOut],
        )

        self.bind_account_list_path = self.register_api(
            '/bind_account_list/',
            'GET',
            self.bind_account_list,
            tenant_path=True,
            auth=GlobalAuth(),
            response=List[AppAccountListItemOut],
        )

        self.account_list_path = self.register_api(
            '/account_list/',
            'GET',
            self.account_list,
            tenant_path=True,
            auth=GlobalAuth(),
            response=UserAppAccountListOut,
        )

        self.bind_path = self.register_api(
            '/bind/',
            'POST',
            self.bind,
            tenant_path=True,
            auth=GlobalAuth(),
            response=ResponseSchema,
        )

        self.unbind_path = self.register_api(
            '/unbind/{id}/',
            'GET',
            self.unbind,
            tenant_path=True,
            auth=GlobalAuth(),
            response=ResponseSchema,
        )

        self.setting_app_list_path = self.register_api(
            '/setting_app_list/',
            'GET',
            self.setting_app_list,
            tenant_path=True,
            auth=GlobalAuth(),
            response=List[AppListItemOut],
        )
        

    def register_pages(self):
        multiaccount_setting_manange_page = pages.TablePage(
            name=_("应用多账号配置管理")
        )
        edit_page = pages.FormPage(name=_("编辑配置"))

        select_app_page.create_actions(
            init_action=actions.DirectAction(
                path=self.list_unsetting_app_path,
                method=actions.FrontActionMethod.GET
            )
        )


        multiaccount_setting_manange_page.create_actions(
            init_action=actions.DirectAction(
                path=self.list_multiaccount_settings_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'create': actions.CreateAction(
                    path=self.add_multiaccount_setting_path
                ),
            },
            local_actions={
                "update": actions.OpenAction(
                    name=_("编辑"),
                    icon="icon-edit",
                    page=edit_page,
                ),
                "delete": actions.DeleteAction(
                    path=self.delete_multiaccount_setting_path,
                ),
            },
        )

        edit_page.create_actions(
            init_action=actions.DirectAction(
                path=self.get_multiaccount_setting_path,
                method=actions.FrontActionMethod.GET
            ),
            global_actions={
                'confirm': actions.ConfirmAction(
                    path=self.update_multiaccount_setting_path
                ),
            }
        )

        self.register_front_pages(multiaccount_setting_manange_page)
        self.register_front_pages(edit_page)
        self.register_front_pages(select_app_page)

        multiaccount_setting_router = routers.FrontRouter(
            path="multiaccount_setting",
            name=_("多账号管理"),
            page=multiaccount_setting_manange_page,
            icon='sync',
        )
        from api.v1.pages.auth_manage import router
        self.register_front_routers(multiaccount_setting_router, router)

        # 用户认证管理

        mine_accounts_bind_page = pages.TablePage(name='应用账号绑定')

        mine_select_app_page.create_actions(
            init_action=actions.DirectAction(
                path=self.setting_app_list_path,
                method=actions.FrontActionMethod.GET
            )
        )

        mine_accounts_bind_page.create_actions(
            init_action=actions.DirectAction(
                path=self.bind_account_list_path,
                method=actions.FrontActionMethod.GET,
            ),
            global_actions={
                'create': actions.CreateAction(
                    path=self.bind_path,
                    name=_("绑定账号")
                ),
            },
            local_actions={
                "delete": actions.DirectAction(
                    name=_("解绑"),
                    path=self.unbind_path,
                    method=actions.FrontActionMethod.GET
                ),
            },
        )

        self.register_front_pages(mine_select_app_page)
        self.register_front_pages(mine_accounts_bind_page)


        from api.v1.pages.mine.auth_manage import page as mine_auth_page
        mine_auth_page.add_pages(mine_accounts_bind_page)

    @operation(AppMultiAccountSettingOutSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def add_multiaccount_setting(self, request, tenant_id: str, data: AppMultiAccountSettingSchema):
        req_data = data.dict()
        app = App.objects.get(id=req_data["app"]["id"])
        setting,_ = AppMultiAccountSetting.objects.get_or_create(app=app)
        setting.bind_url = data.bind_url
        setting.unbind_url = data.unbind_url
        setting.save()
        return self.success(data={})

    @operation(List[AppMultiAccountSettingListItemOutSchema], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def list_multiaccount_settings(self, request, tenant_id: str, filter_data: AppMultiAccountSettingListFilterSchema = Query(...)):
        apps = App.active_objects.filter(tenant__id=tenant_id)

        if filter_data.app__name:
            apps = apps.filter(name=filter_data.app__name)

        app_ids = [app.id for app in apps.all()]

        settings = AppMultiAccountSetting.objects.filter(app__in=app_ids).all()
        return [
            {
                "id": setting.id,
                "app": setting.app.name,
                "bind_url": setting.bind_url,
                "unbind_url": setting.unbind_url
            } for setting in settings
        ]

    @operation(AppMultiAccountSettingDetailOutSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def get_multiaccount_setting(self, request, tenant_id: str, id: str):
        setting = AppMultiAccountSetting.objects.get(id=id)
        return self.success(data={
            "app": setting.app.name,
            "bind_url": setting.bind_url,
            "unbind_url": setting.unbind_url
        })

    @operation(AppMultiAccountSettingOutSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def update_multiaccount_setting(self, request, tenant_id: str, id: str, data: AppMultiAccountSettingUpdateSchema):
        setting = AppMultiAccountSetting.objects.get(id=id)
        setting.bind_url = data.bind_url
        setting.unbind_url = data.unbind_url
        setting.save()
        return self.success()

    @operation(AppMultiAccountSettingOutSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def delete_multiaccount_setting(self, request, tenant_id: str, id: str):
        setting = AppMultiAccountSetting.objects.get(id=id)
        setting.delete()
        return self.success()

    @operation(List[AppListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    @paginate(CustomPagination)
    def unsetting_app_list(self, request, tenant_id: str):
        settings = AppMultiAccountSetting.objects.filter(app__tenant__id=tenant_id).all()
        setting_apps = [setting.app.id for setting in settings]

        all_apps = App.active_objects.filter(tenant__id=tenant_id).exclude(id__in=setting_apps).all()

        return [
            {
                "id": app.id.hex,
                "name": app.name
            } for app in all_apps
        ]
    
    @operation(List[AppAccountListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN,NORMAL_USER])
    @paginate(CustomPagination)
    def bind_account_list(self, request, tenant_id: str):
        acs = UserApplicationAccount.objects.filter(user=request.user).all()
        return [
            {
                "id": ac.id,
                "name": ac.app.name,
                "username": ac.username
            } for ac in acs
        ]

    @operation(UserAppAccountListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN,NORMAL_USER])
    def account_list(self, request, tenant_id: str, app_id:str):
        app = App.objects.get(id=app_id)
        acs = UserApplicationAccount.objects.filter(user=request.user,app=app).all()

        return self.success(
            data=[
                {
                    "platform_user_id": request.user.id,
                    "token": ac.token
                } for ac in acs
            ]
        )

    @operation(ResponseSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN,NORMAL_USER])
    def bind(self, request, tenant_id: str, data:BindInSchema):
        req_data = data.dict()
        app = App.objects.get(id=req_data["app"]["id"])

        setting = AppMultiAccountSetting.objects.filter(app=app).first()

        if setting.bind_url:
            rs = requests.post(
                url = setting.bind_url,
                json={
                    "platform_user_id": request.user.id,
                    "username": req_data["username"],
                    "password": req_data["password"]
                },
                timeout=1.0
            )
            try:
                res_data = json.loads(rs.content)
            except Exception as err:
                return self.error(ErrorCode.AUHENTICATION_FAILED)

            account = UserApplicationAccount(
                user=request.user,
                app=app,
                token=res_data,
                username=req_data["username"]
            )
            account.save()
        else:
            return self.error(ErrorCode.NOT_CONFIG)

        return self.success()
    
    @operation(ResponseSchema, roles=[TENANT_ADMIN, PLATFORM_ADMIN,NORMAL_USER])
    def unbind(self, request, tenant_id: str, id:str):
        ac = UserApplicationAccount.objects.get(id=id)

        setting = AppMultiAccountSetting.objects.filter(app=ac.app).first()
        if setting.unbind_url:
            requests.post(
                url = setting.unbind_url,
                json={
                    "platform_user_id": request.user.id,
                    "token": ac.token,
                },
                timeout=1.0
            )
        else:
            return self.error(ErrorCode.NOT_CONFIG)
        ac.delete()
        return self.success()

    @operation(List[AppListItemOut], roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    @paginate(CustomPagination)
    def setting_app_list(self, request, tenant_id: str):
        settings = AppMultiAccountSetting.objects.filter(app__tenant__id=tenant_id).all()
        setting_apps = [setting.app for setting in settings]

        return [
            {
                "id": app.id.hex,
                "name": app.name
            } for app in setting_apps
        ]


extension = MultipleAccountExtension()

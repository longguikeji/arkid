from arkid.core import actions, extension, pages, routers
from arkid.core.api import operation
from arkid.core.event import AUTH_SUCCESS
from arkid.core.models import User 
from arkid.core.translation import gettext_default as _
from arkid.core.constants import *
from .schema import *
from api.v1.pages.user_manage.user_list import page as user_list_page
from .errorcode import ErrorCode

class AccountActiveExtension(extension.Extension):
    
    def load(self):
        super().load()
        
        self.account_active_switch_path = self.register_api(
            '/user/{id}/account_active_switch/',
            'GET',
            self.account_active_switch,
            tenant_path=True,
            auth=None,
            response=AccountActiveSwitchOut,
        )
        
        self.inactive_account_list_path = self.register_api(
            '/inactive_account_list/',
            'GET',
            self.inactive_account_list,
            tenant_path=True,
            auth=None,
            response=InactiveAccountListOut,
        )
        
        user_list_page.add_local_actions(
            actions.DirectAction(
                name=_('冻结'),
                path=self.account_active_switch_path,
                method=actions.FrontActionMethod.GET,
            )
        )
        
        self.listen_event(AUTH_SUCCESS,self.auth_success_check)
        
        self.register_pages()
    
    @operation(AccountActiveSwitchOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def account_active_switch(self, request, tenant_id: str, id:str):
        """ 重置账号
        """
        user = User.valid_objects.get(id=id)
        user.is_active = not user.is_active
        user.save()
        return self.success(data={"is_active":user.is_active})
    
    @operation(InactiveAccountListOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def inactive_account_list(self, request, tenant_id: str):
        """ 重置账号
        """
        users = User.expand_objects.filter(tenant=request.tenant,is_active=False,is_del=False).all()
        return self.success(data=list(users))
    
    def register_pages(self):
        inactive_user_list_page = pages.TablePage(
            name=_("冻结用户名单")
        )
        inactive_user_list_page.create_actions(
            init_action=actions.DirectAction(
                path=self.inactive_account_list_path,
                method=actions.FrontActionMethod.GET,
            ),
            local_actions={
                "active": actions.DirectAction(
                    name=_('解冻'),
                    path=self.account_active_switch_path,
                    method=actions.FrontActionMethod.GET,
                ),
            },
        )
        self.register_front_pages(inactive_user_list_page)
        inactive_user_list_router = routers.FrontRouter(
            path="inactive_user_list",
            name=_("冻结用户名单"),
            page=inactive_user_list_page,
            icon='list',
        )
        from api.v1.pages.user_manage import router
        self.register_front_routers(inactive_user_list_router, router)
        
    
    def auth_success_check(self,event,*argc,**kwargs):
        user = event.data["user"]
        if not user.is_active:
            return False, self.error(ErrorCode.USER_INACTIVE)
        return True,None
    
extension = AccountActiveExtension()
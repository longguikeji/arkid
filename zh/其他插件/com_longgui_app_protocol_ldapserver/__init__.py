
import json
import re
from typing_extensions import Self

from django.conf import settings
from arkid.config import get_app_config
from arkid.core.api import GlobalAuth, operation
from arkid.core.error import ErrorDict, SuccessDict
from arkid.core.event import Event, dispatch_event
from arkid.core.extension.app_protocol import AppProtocolExtension
from arkid.core.models import User, UserGroup
from arkid.core.token import refresh_token
from arkid.extension.models import TenantExtension, TenantExtensionConfig
from arkid.core.constants import *
from arkid.core import pages, actions, routers
from arkid.core.translation import gettext_default as _
from .schema import *
from .error import ErrorCode


class LDAPServerExtension(AppProtocolExtension):

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
        UserAttributeMapping = create_extension_schema(
            "UserAttributeMapping",
            __file__,
            fields=[
                (
                    "key",
                    str,
                    Field(
                        title=_("映射名")
                    )
                ),
                (
                    "value",
                    str,
                    Field(
                        path=self.user_fields_path,
                        method="get",
                        format="autocomplete",
                        title=_("字段名")
                    )
                )
            ]
        )

        GroupAttributeMapping = create_extension_schema(
            "GroupAttributeMapping",
            __file__,
            fields=[
                (
                    "key",
                    str,
                    Field(
                        title=_("映射名")
                    )
                ),
                (
                    "value",
                    str,
                    Field(
                        option_action={
                            "path": self.group_fields_path,
                            "method": actions.FrontActionMethod.GET.value,
                        },
                        type="string",
                        format="autocomplete",
                        title=_("字段名")
                    )
                )
            ]
        )

        LDAPApplicationSchema = create_extension_schema(
            'LDAPApplicationSchema',
            __file__,
            [
                (
                    "people",
                    List[UserAttributeMapping],
                    Field(
                        title=_("用户信息字段映射"),
                        format='dynamic',
                        type="array",
                        default=[
                            {
                                "key": "cn",
                                "value": "username"
                            },
                            {
                                "key": "uid",
                                "value": "id"
                            }
                        ]
                    )
                ),
                (
                    "group",
                    List[GroupAttributeMapping],
                    Field(
                        title=_("群组信息字段映射"),
                        format='dynamic',
                        type="array",
                        default=[
                            {
                                "key": "cn",
                                "value": "id"
                            },
                            {
                                "key": "name",
                                "value": "name"
                            }
                        ]
                    )
                )

            ],
            base_schema=LDAPApplicationSettingsSchema
        )
        self.register_settings_schema(
            LDAPApplicationSchema
        )

    @operation(LDAPServerDataSearchOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def data_search(self, request, tenant_id: str, data: LDAPServerDataSearchIn):
        """数据搜索

        Args:
            request (Request): 请求
            tenant_id (str): 租户ID
            data (LDAPServerDataSearchIn): 请求数据

        Returns:
            list[dict]: 列表
        """
        print(request.body)
        tenant = request.tenant
        dn = data.dn
        scope = data.scope

        res = []
        # 处理dn 去掉空格并分割
        dn.replace(" ", "")
        items = dn.split(",")
        item = items[0]

        dc_suf = ","+",".join(items[1:])

        match_params = re.findall("(.*)=(.*)", item)
        if match_params:
            match_params = match_params[0]
        print(f"-------------{dc_suf}------{scope}---------------")
        if scope == "base":
            # 查询自身
            if match_params[0] == "cn":
                if "ou=people" in dc_suf:
                    res.append(
                        self.user_find_by_name(
                            tenant,
                            match_params[1],
                            dc_suf
                        )
                    )
                elif "ou=group" in dc_suf:
                    res.append(
                        self.group_find_by_id(
                            tenant,
                            match_params[1],
                            dc_suf
                        )
                    )
            elif match_params[0] == "ou":
                if match_params[1] == "people":
                    res.append(
                        {
                            "dn": f"ou=people{dc_suf}",
                            "attributes": {
                                "objectClass": ["container"],
                                "hassubordinates": True,
                            }
                        }
                    )
                elif match_params[1] == "group":
                    res.append(
                        {
                            "dn": f"ou=group{dc_suf}",
                            "attributes": {
                                "objectClass": ["container"],
                                "hassubordinates": True,
                            }
                        }
                    )
            elif match_params[0] == "o":
                res.append(
                    {
                        "dn": f"o={match_params[1]}{dc_suf}",
                        "attributes": {
                            "objectClass": ["top", "root", "tenant"],
                            "name": tenant.name,
                            "slug": tenant.slug,
                            "hassubordinates": True,
                        }
                    }
                )
            elif match_params[0] == "dc":
                res.append(
                    {
                        "dn": f"dc={match_params[1]}{dc_suf}",
                        "attributes": {
                            "objectClass": ["top", "root", "domain"],
                            "hassubordinates": True,
                        }
                    }
                )
        elif scope == "one":
            # 查询次一级数据
            if match_params[0] == "cn":
                if "ou=people" in dc_suf:
                    pass
                elif "ou=group" in dc_suf:
                    res.extend(
                        self.group_users(
                            tenant,
                            match_params[1],
                            dc_suf
                        )
                    )
            elif match_params[0] == "ou":
                if match_params[1] == "people":
                    res.extend(self.find_all_users(tenant, dc_suf))
                elif match_params[1] == "group":
                    res.extend(self.find_all_groups(tenant, dc_suf))
            elif match_params[0] == "dc":
                res.append(
                    {
                        "dn": f"o={tenant_id}, {match_params[0]}={match_params[1]}{dc_suf}",
                        "attributes": {
                            "objectClass": ["container"],
                            "hassubordinates": True,
                        }
                    }
                )
            elif match_params[0] == "o":
                res.append(
                    {
                        "dn": f"ou=people, {match_params[0]}={match_params[1]}{dc_suf}",
                        "attributes": {
                            "objectClass": ["container"],
                            "hassubordinates": True,
                        }
                    }
                )
                res.append(
                    {
                        "dn": f"ou=group, {match_params[0]}={match_params[1]}{dc_suf}",
                        "attributes": {
                            "objectClass": ["container"],
                            "hassubordinates": True,
                        }
                    }
                )
        else:
            # 暂不支持 抛出错误
            return self.error(
                ErrorCode.UNSUPPORTED_SCOPE
            )
        return self.success(
            data=res
        )

    def find_all_groups(self, tenant, base_dn):
        """查找租户下所有群组

        Args:
            tenant (Tenant):租户
            base_dn (str): 基础域名

        Returns:
            list[dict]: 群组描述列表
        """
        groups = UserGroup.expand_objects.filter(tenant=tenant).all()
        return [{
            "dn": f"cn={group['id']},ou=group{base_dn}",
            "attributes": self.get_attributes(tenant, group, "group")
        } for group in groups]

    def find_all_users(self, tenant, base_dn):
        """查找租户下所有用户

        Args:
            tenant (Tenant):租户
            base_dn (str): 基础域名

        Returns:
            list[dict]: 用户描述列表
        """
        users = User.expand_objects.filter(tenant=tenant).all()

        return [{
            "dn": f"cn={user['username']},ou=people{base_dn}",
            "attributes": self.get_attributes(tenant, user, "people")
        } for user in users]

    def user_find_by_name(self, tenant, username, base_dn):
        """通过username寻找用户

        Args:
            tenant (Tenant):租户
            username (str): 用户名
            base_dn (str): 基础域名

        Returns:
            dict: 用户描述
        """
        user = User.expand_objects.filter(
            tenant=tenant, username=username).first()

        if not user:
            return

        return {
            "dn": f"cn={user['username']}{base_dn}",
            "attributes": self.get_attributes(tenant, user, "people")
        }

    def group_find_by_id(self, tenant, id, base_dn):
        """通过id寻找群组

        Args:
            tenant (Tenant):租户
            id (str): 群组ID
            base_dn (str): 基础域名

        Returns:
            dict: 群组描述
        """
        group = UserGroup.expand_objects.get(id=id)

        return {
            "dn": f"cn={group['id']}{base_dn}",
            "attributes": self.get_attributes(tenant, group, "group")
        }

    def group_users(self, tenant, id, base_dn):
        """查找租户下指定群组所有用户

        Args:
            tenant (Tenant):租户
            id (str): 群组ID
            base_dn (str): 基础域名

        Returns:
            list[dict]: 用户描述列表
        """
        group = UserGroup.active_objects.get(id=id)
        base_dn = base_dn.replace("ou=group", "ou=people")
        return [
            {
                "dn": f"cn={user['username']}{base_dn}",
                "attributes": self.get_attributes(tenant, user, "people")
            } for user in User.expand_objects.filter(
                id__in=[t.id for t in group.users.all()]
            ).all()
        ]

    def get_attributes(self, tenant, obj, key):
        """获取对象中指定的属性

        Args:
            tenant (Tenant):租户
            obj (Object): 用户或者群组对象
            key (str): 描述，群组或者用户

        Returns:
            dict: 属性字典
        """
        attributes = {}
        attribute_mappings = self.get_attribute_mappings(
            tenant,
            key
        )
        for k in attribute_mappings.keys():
            value = obj.get(attribute_mappings[k], None)
            if isinstance(value, UUID):
                value = value.hex
            attributes[k] = value

        if key == "people":
            attributes["objectClass"] = ["person"]
            attributes["hassubordinates"] = False
        else:
            attributes["objectClass"] = ["group"]
            attributes["hassubordinates"] = True

        return attributes

    def get_attribute_mappings(self, tenant, key="people"):
        """
        获取自定义字段
        """
        extension = self.model
        settings = TenantExtension.active_objects.filter(
            extension=extension,
            tenant=tenant
        ).first()

        settings_attribute_list = settings.settings.get(key, [])
        attribute_mappings = {}
        for item in settings_attribute_list:
            attribute_mappings[item["key"]] = item["value"]
        return attribute_mappings

    @operation(LDAPServerLoginOut, use_id=True)
    def login(self, request, tenant_id: str, data: LDAPServerLoginIn):
        """LDAP SERVER 登录请求
        """
        tenant = request.tenant
        request_id = request.META.get('request_id')

        settings = TenantExtension.active_objects.filter(
            extension=self.model,
            tenant=tenant
        ).first()

        if not settings:
            return self.error(
                ErrorCode.NO_ACTIVE_EXTENSION_SETTINGS
            )

        if not settings.settings["server"]["BASE_DN"] == data.basedn:
            return self.error(
                ErrorCode.DN_NOT_MATCH
            )

        login_config = TenantExtensionConfig.valid_objects.filter(
            tenant=tenant,
            type="password",
        ).first()

        request.POST["config_id"] = login_config.id.hex

        responses = dispatch_event(Event(
            tag="com.longgui.auth.factor.password.auth", tenant=tenant, request=request, uuid=request_id))
        if not responses:
            return ErrorDict(ErrorCode.AUTH_EXTENSION_IS_DISACTIVELY)

        useless, (user, useless) = responses[0]

        # 生成 token
        token = refresh_token(user)

        return self.success({'token': token})

    @operation(LDAPServerSettingsOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def settings(self, request, tenant_id: str):
        """配置
        """
        settings = TenantExtension.active_objects.filter(
            extension=self.model,
            tenant=request.tenant
        ).first()

        if not (settings and settings.settings.get("server", None)):
            return self.error(
                ErrorCode.NO_ACTIVE_EXTENSION_SETTINGS
            )

        return self.success(
            data={
                "ARKID_DOMAIN": get_app_config().get_host(),
                "BASE_DN": settings.settings["server"]["BASE_DN"],
                "LOGIN_USERNAME_FORMAT": "cn={username}, ou=people, o="+request.tenant.id.hex+", " + settings.settings["server"]["BASE_DN"]
            }
        )

    def register_extension_api(self):
        """注册插件API
        """
        self.login_path = self.register_api(
            '/login/',
            'POST',
            self.login,
            tenant_path=True,
            auth=None,
            response=LDAPServerLoginOut,
        )

        self.search_path = self.register_api(
            '/search/',
            'POST',
            self.data_search,
            tenant_path=True,
            auth=GlobalAuth(),
            response=LDAPServerDataSearchOut,
        )

        self.settings_path = self.register_api(
            '/settings/',
            'GET',
            self.settings,
            tenant_path=True,
            auth=GlobalAuth(),
            response=LDAPServerSettingsOut,
        )

        self.user_fields_path = self.register_api(
            '/user_fields/',
            'GET',
            self.user_fields,
            tenant_path=False,
            auth=GlobalAuth(),
            response=UserFieldsOut,
        )

        self.group_fields_path = self.register_api(
            '/group_fields/',
            'GET',
            self.group_fields,
            tenant_path=False,
            auth=GlobalAuth(),
            response=GroupFieldsOut,
        )

        self.tenant_search_path = self.register_api(
            '/tenant_search/',
            'POST',
            self.search_tenant,
            tenant_path=True,
            auth=GlobalAuth(),
            response=LDAPSearchTenantOut,
        )

        self.find_tenant_path = self.register_api(
            '/find_tenant/',
            'GET',
            self.find_tenant,
            tenant_path=True,
            auth=GlobalAuth(),
            response=LDAPFindTenantOut,
        )

        self.find_tenant_users_path = self.register_api(
            '/find_tenant_users/',
            'GET',
            self.find_tenant_users,
            tenant_path=True,
            auth=GlobalAuth(),
            response=LDAPSearchTenantUserOut,
        )

    def register_pages(self):
        data_sync_page = pages.FormPage(
            name=_("LDAP SERVER")
        )
        data_sync_page.create_actions(
            init_action=actions.DirectAction(
                path=self.settings_path,
                method=actions.FrontActionMethod.GET,
            ),
        )
        self.register_front_pages(data_sync_page)
        data_sync_router = routers.FrontRouter(
            path="ldap_server",
            name=_("LDAP SERVER"),
            page=data_sync_page,
            icon='sync',
        )
        from api.v1.pages.data_source_manage import router
        self.register_front_routers(data_sync_router, router)

    @operation(UserFieldsOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def user_fields(self, request):
        """用户模型字段列表
        """
        data = ["id"]
        data.extend([key for key, value in User.key_fields.items()])
        return self.success(data)

    @operation(GroupFieldsOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def group_fields(self, request):
        """组模型字段列表
        """
        data = ["id", "name"]
        return self.success(data)

    @operation(LDAPSearchTenantOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def search_tenant(self, request, tenant_id: str):
        if (request.tenant.is_platform_tenant):
            # 返回所有可用租户
            rs = [
                {
                    "id": str(tenant.id.hex),
                    "name": tenant.name,
                    "slug": tenant.slug
                } for tenant in Tenant.valid_objects.all()
            ]
            return self.success(data=rs)

        else:
            # 返回当前租户
            return self.success(data=[{
                "id": str(request.tenant.id.hex),
                "name": request.tenant.name,
                "slug": request.tenant.slug
            }])

    @operation(LDAPSearchTenantUserOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def find_tenant_users(self, request, tenant_id: str):
        users = request.tenant.users.filter(is_active=True, is_del=False).all()
        # 返回当前租户
        return self.success(data=[{
            "id": str(user.id.hex),
            "username": user.username,
            "avatar": user.avatar
        } for user in users])

    @operation(LDAPFindTenantOut, roles=[TENANT_ADMIN, PLATFORM_ADMIN, NORMAL_USER])
    def find_tenant(self, request, tenant_id: str):
        return self.success(data={
            "id": str(request.tenant.id.hex),
            "name": request.tenant.name,
            "slug": request.tenant.slug
        })


extension = LDAPServerExtension()

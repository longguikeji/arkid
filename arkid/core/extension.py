from abc import abstractclassmethod
from django.urls import include, re_path
from pathlib import Path
from arkid import config
from collections import OrderedDict
from django.apps import apps
from django.conf import settings
from django.core import management
from arkid.core import api as core_api, pages as core_page, routers as core_routers, event as core_event
from arkid.core import urls as core_urls, expand as core_expand, models as core_models, translation as core_translation
from arkid.extension.models import TenantExtensionConfig, Extension


app_config = config.get_app_config()

Event = core_event.Event
EventType = core_event.EventType

class Extension:

    def __init__(self, package, version, description, labels, homepage, logo, author) -> None:
        self.package = package
        self.version = version
        self.description = description
        self.labels = labels
        self.homepage = homepage
        self.logo = logo
        self.author = author
        self.name = self.package.replace('.', '_')
        self.urls = []
        self.extend_fields = []
        self.events = []
        self.event_tags = []
        self.extend_apis = []
        self.front_routers = []
        self.front_pages = []
        self.lang_code = None

    @property
    def ext_dir(self):
        return self._ext_dir

    @ext_dir.setter
    def ext_dir(self, value: str):
        self._ext_dir = value

    @property
    def full_name(self):
        return f'{Path(self.ext_dir).parent}.{self.name}'

    def migrate_extension(self) -> None:
        extension_migrate_foldname = Path(self.ext_dir) / 'migrations'
        if not extension_migrate_foldname.exists():
            return
        settings.INSTALLED_APPS += (self.full_name, )
        apps.app_configs = OrderedDict()
        apps.apps_ready = apps.models_ready = apps.loading = apps.ready = False
        apps.clear_cache()
        apps.populate(settings.INSTALLED_APPS)

        # management.call_command('makemigrations', self.name, interactive=False)
        print(f'Migrate {self.name}')
        management.call_command('migrate', self.name, interactive=False)

    def register_routers(self, urls_ext, tenant_urls=False):
        if tenant_urls:
            urls_ext = [re_path(r'tenant/(?P<tenant_uuid>[\w-]+)/', include((urls_ext, 'extension'), namespace=f'{self.name}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)
        else:
            urls_ext = [re_path('', include((urls_ext, 'extension'), namespace=f'{self.name}'))]
            self.urls.extend(urls_ext)
            core_urls.register(urls_ext)

    def register_extend_field(self, model_cls, model_field, alias=None):
        if issubclass(model_cls, core_expand.TenantExpandAbstract):
            table = core_models.Tenant._meta.db_table
        elif issubclass(model_cls, core_expand.UserExpandAbstract):
            table = core_models.User._meta.db_table
        elif issubclass(model_cls, core_expand.UserGroupExpandAbstract):
            table = core_models.UserGroup._meta.db_table
        elif issubclass(model_cls, core_expand.AppExpandAbstract):
            table = core_models.App._meta.db_table
        elif issubclass(model_cls, core_expand.AppGroupExpandAbstract):
            table = core_models.AppGroup._meta.db_table
        elif issubclass(model_cls, core_expand.PermissionExpandAbstract):
            table = core_models.Permission._meta.db_table
        elif issubclass(model_cls, core_expand.ApproveExpandAbstract):
            table = core_models.Approve._meta.db_table
        elif issubclass(model_cls, core_expand.TenantConfigExpandAbstract):
            table = core_models.TenantConfig._meta.db_table
        else:
            raise Exception('非法的扩展字段类对应的父类')

        data = OrderedDict(
            table = table,
            field = alias or model_field,
            extension = self.name,
            extension_model = model_cls._meta.model_name,
            extension_table = model_cls._meta.db_table,
            extension_field = model_field,
        )

        self.extend_fields.append(data)
        core_expand.field_expand_map.append(data)

    def listen_event(self, tag, func):
        def signal_func(event, **kwargs2):
            # 判断租户是否启用该插件
            # tenant
            # 插件名 tag
            # func.__module__ 'extension_root.abc.xx'
            # kwargs2.pop()
            # Extension.
            return func(event=event, **kwargs2)

        core_event.listen_event(tag, signal_func, listener=self)
        self.events.extend((tag, signal_func))        

    def register_event(self, tag, name, data_model=None, description=''):
        tag = self.package + '_' + tag
        core_event.register_event(tag, name, data_model, description)
        self.event_tags.append(tag)
        return tag

    def dispatch_event(self, event):
        return core_event.dispatch_event(event=event, sender=self)

    def register_extend_api(self, api_schema_cls, **field_definitions):
        core_api.add_fields(api_schema_cls, **field_definitions)
        self.extend_apis.append((api_schema_cls, field_definitions.keys()))
        
    def register_languge(self, lang_code:str = 'en', lang_maps={}):
        self.lang_code = lang_code
        if lang_code in core_translation.extension_lang_maps.keys():
            core_translation.extension_lang_maps[lang_code][self.name] = lang_maps
        else:
            core_translation.extension_lang_maps[lang_code] = {}
            core_translation.extension_lang_maps[lang_code][self.name] = lang_maps
        core_translation.lang_maps = core_translation.reset_lang_maps()
        
    def register_front_routers(self, router, primary=''):
        """
        primary: 一级路由名字，由 core_routers 文件提供定义
        """
        router.path = self.package
        router.change_page_tag(self.package)

        for old_router, old_primary in self.front_routers:
            if old_primary == primary:
                self.front_routers.remove((old_router, old_primary))
                core_routers.unregister_front_routers(old_router, old_primary)

        core_routers.register_front_routers(router, primary)
        self.front_routers.append((router, primary))

    def register_front_pages(self, page):
        """
        primary: 一级路由名字，由 core_routers 文件提供定义
        """
        page.tag = self.package + '_' + page.tag

        core_page.register_front_pages(page)
        self.front_pages.append(page)

    def get_tenant_configs(self, tenant):
        ext = Extension.objects.filter(package=self.package, version=self.version).first()
        configs = TenantExtensionConfig.objects.filter(tenant=tenant, extension=ext).all()
        return configs

    def get_config_by_uuid(self, uuid):
        return TenantExtensionConfig.objects.get(uuid=uuid)
    
    def update_tenant_config(self, uuid,  config):
        TenantExtensionConfig.objects.get(uuid=uuid).update(config=config)

    def create_tenant_config(self, tenant, config):
        ext = Extension.objects.filter(package=self.package, version=self.version).first()
        TenantExtensionConfig.objects.create(tenant=tenant, extension=ext, config=config)

    def load(self):
        self.migrate_extension()
        # self.install_requirements() sys.modeles

    def unload(self):
        core_urls.unregister(self.urls)
        for tag, func in self.events:
            core_event.unlisten_event(tag, func)
        for field in self.extend_fields:
            core_expand.field_expand_map.remove(field)
        for api_schema_cls, fields in self.extend_apis:
            core_api.remove_fields(api_schema_cls, fields)
        for old_router, old_primary in self.front_routers:
            core_routers.unregister_front_routers(old_router, old_primary)
        for page in self.front_pages:
            core_page.unregister_front_pages(page)
        for tag in self.event_tags:
            core_event.unregister_event(tag)

        if self.lang_code:
            core_translation.extension_lang_maps[self.lang_code].pop(self.name)
            if not core_translation.extension_lang_maps[self.lang_code]:
                core_translation.extension_lang_maps.pop(self.lang_code)
            core_translation.lang_maps = core_translation.reset_lang_maps()


class AuthFactorExtension(Extension):
    LOGIN = 'login'
    REGISTER = 'register'
    RESET_PASSWORD = 'password'

    def load(self):
        super().load()
        self.auth_event_tag = self.register_event('auth', '认证')
        self.listen_event(self.auth_event_tag, self.authenticate)
        self.register_event_tag = self.register_event('register', '注册')
        self.listen_event(self.register_event_tag, self.register)
        self.password_event_tag = self.register_event('password', '重置密码')
        self.listen_event(self.password_event_tag, self.reset_password)
        self.listen_event(core_event.CREATE_LOGIN_PAGE_AUTH_FACTOR, self.create_response)

    @abstractclassmethod
    def authenticate(self, event, **kwargs):
        pass

    def auth_success(self, user):
        return user
    
    def auth_failed(self, event):
        core_event.remove_event_uuid(event)
        core_event.break_event_loop(event.data)

    @abstractclassmethod
    def register(self, event, **kwargs):
        pass
    
    @abstractclassmethod
    def reset_password(self, event, **kwargs):
        pass
    
    def create_response(self, event, **kwargs):
        self.data = {
            self.LOGIN: {
                'forms':[],
                'bottoms':[],
                'expand':{},
            },
            self.REGISTER: {
                'forms':[],
                'bottoms':[],
                'expand':{},
            },
            self.RESET_PASSWORD: {
                'forms':[],
                'bottoms':[],
                'expand':{},
            },
        }
        configs = self.get_tenant_configs(event.tenant)
        for config in configs:
            if config.is_login:
                self.create_login_page(event, config)
            if config.is_register:
                self.create_register_page(event, config)
            if config.is_password:
                self.create_password_page(event, config)
        self.create_other_page(event, config)
        return self.data
        
    def add_page_form(self, config, page_name, label, items, submit_url=None, submit_label=None):
        default = {
            "login": ("登录", "/api/v1/auth/?tenant=tenant_uuid"),
            "register": ("登录", "/api/v1/register/?tenant=tenant_uuid"),
            "password": ("登录", "/api/v1/reset_password/?tenant=tenant_uuid"),
        }
        if not submit_label:
            submit_label, useless = default.get(page_name)
        if not submit_url:
            useless, submit_url = default.get(page_name)

        items.append({"type": "hidden", "name": "config_uuid", "value": config.uuid})
        self.data[page_name]['forms'].append({
            'label': label,
            'items': items,
            'submit': {'label': submit_label, 'http': {'url': submit_url, 'method': "post"}}
        })

    def add_page_bottoms(self, page_name, bottoms):
        self.data[page_name]['bottoms'].append(bottoms)

    def add_page_extend(self, page_name, buttons, title=None):
        if not self.data[page_name].get('extend'):
            self.data[page_name]['extend'] = {}

        self.data[page_name]['extend']['title'] = title
        self.data[page_name]['extend']['buttons'].append(buttons)

    @abstractclassmethod
    def create_login_page(self, event, config):
        pass

    @abstractclassmethod
    def create_register_page(self, event, config):
        pass

    @abstractclassmethod
    def create_password_page(self, event, config):
        pass

    @abstractclassmethod
    def create_other_page(self, event, config):
        pass
    
    def get_current_config(self, event):
        config_uuid = event.POST.get('config_uuid')
        return self.get_config_by_uuid(config_uuid)
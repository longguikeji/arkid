from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from pydantic import Field
from .models import NginxAPP
from arkid.core.event import CREATE_APP, UPDATE_APP, DELETE_APP
import os
from arkid.common.logger import logger
from arkid.config import get_app_config
from typing import Optional
from .template import NginxConfTemplate
from urllib.parse import urlparse
from arkid.core.models import ExpiringToken, Tenant, App
from arkid.core.perm.permission_data import PermissionData


class AppProxyNginxExtension(Extension):
    def load(self):
        self.register_extend_field(NginxAPP, 'is_intranet_url')
        from api.v1.schema.app import (
            AppUpdateIn,
            CreateAppIn,
            AppListItemOut,
            AppItemOut,
        )

        self.register_extend_api(
            AppUpdateIn,
            CreateAppIn,
            AppListItemOut,
            AppItemOut,
            is_intranet_url=(Optional[bool], Field(default=False, title='是否内网地址')),
        )
        self.listen_event(CREATE_APP, self.create_app)
        self.listen_event(UPDATE_APP, self.update_app)
        self.listen_event(DELETE_APP, self.delete_app)
        self.listen_event(
            'api_v1_views_mine_get_mine_apps_with_group', self.change_desktop_apps_url
        )
        self.register_api(
            '/nginx_auth/{app_id}',
            'GET',
            self.nginx_auth,
            tenant_path=True,
            auth=None,
            response={200: None, 401: None},
        )
        super().load()

    def nginx_auth(self, request, tenant_id, app_id):
        token = request.COOKIES.get("arkid_token", "")
        if not token:
            logger.info(f"No arkid_token found")
            return 401, None
        try:
            exp_token = ExpiringToken.objects.get(token=token)

            if not exp_token.user.is_active:
                raise Exception(_('User inactive or deleted', '用户无效或被删除'))

            if exp_token.expired(request.tenant):
                raise Exception(_('Token has expired', '秘钥已经过期'))

        except ExpiringToken.DoesNotExist:
            logger.error('Invalid token')
            return 401, None
        except Exception as err:
            logger.error(err)
            return 401, None

        user = exp_token.user
        app = App.active_objects.filter(id=app_id).first()

        if not app:
            logger.info(f"No such app: {app_id}")
            return 401, None

        permissiondata = PermissionData()
        permission = app.entry_permission
        if not permission:
            logger.info("没有找到入口权限")
            return 401, None
        result = permissiondata.permission_check_by_sortid(
            permission, user, app, tenant_id
        )
        if not result:
            logger.info("没有获得授权使用")
            return 401, None

        return 200, None

    def change_desktop_apps_url(self, event, **kwargs):
        logger.info('App proxy nginx is handing desktop app url...')
        apps = event.response.get("items")
        for app in apps:
            nginx_app = NginxAPP.valid_objects.filter(target=app).first()
            if not nginx_app:
                continue
            if nginx_app.is_intranet_url:
                config = get_app_config()
                frontend_url = config.get_frontend_host(schema=True)
                u = urlparse(frontend_url)
                netloc = f'{app.id.hex}.{u.netloc}'
                app_url = u._replace(netloc=netloc).geturl()
                app.url = f'{app_url}'

    def create_app(self, event, **kwargs):
        logger.info('App proxy nginx is handing create app...')
        self.update_or_create_nginx_conf(event)

    def update_app(self, event, **kwargs):
        logger.info('App proxy nginx is handing update app...')
        self.update_or_create_nginx_conf(event)

    def delete_app(self, event, **kwargs):
        logger.info('App proxy nginx is handing delete app...')
        self.delete_nginx_conf(event)

    def update_or_create_nginx_conf(self, event):
        frontend_url = get_app_config().get_frontend_host(schema=True)
        app = event.data
        u = urlparse(frontend_url)
        app_server_name = f'{app.id.hex}.{u.hostname}'
        tenant_id = event.tenant.id.hex
        app_id = app.id.hex
        port = 80

        if not app.is_intranet_url:
            logger.info(f'Not Intranet URL: is_intranet_url: {app.is_intranet_url}')
            return
        base_dir = '/nginx/'
        if not os.path.exists(base_dir):
            logger.error(f'App proxy nginx conf directory: {base_dir} does not exists')
            return
        file_name = f"{app.id.hex}.conf"
        file_path = os.path.join(base_dir, file_name)
        logger.info(f'App proxy nginx start to write nginx conf file: {file_path}')
        arkid_be_host = os.environ.get("ARKIDBESVC")
        if not arkid_be_host:
            arkid_be_host = u.netloc
        try:
            with open(file_path, 'w') as f:
                values = {
                    'app_server_name': app_server_name,
                    'port': port,
                    'app_proxy_url': app.url,
                    'nginx_auth_url': f'http://{arkid_be_host}/api/v1/tenant/{tenant_id}/com_longgui_app_proxy_nginx/nginx_auth/{app_id}',
                }
                content = NginxConfTemplate.substitute(values)
                f.write(content)
        except Exception as e:
            logger.error(
                f'App proxy nginx write nginx conf file: {file_path} failed: {e}'
            )
        else:
            logger.info(f'App proxy nginx write nginx conf file: {file_path} success!')

    def delete_nginx_conf(self, event):
        app = event.data
        nginx_app = NginxAPP.objects.filter(target=app).first()
        if nginx_app:
            nginx_app.delete()
        else:
            return

        base_dir = '/nginx/'
        file_name = f"{app.id.hex}.conf"
        file_path = os.path.join(base_dir, file_name)
        if not os.path.exists(file_path):
            logger.error(f'App proxy nginx conf file: {file_path} does not exists')
            return
        try:
            os.remove(file_path)
        except Exception as e:
            logger.error(f'Delete nginx conf file {file_path} failed: {e}')
        else:
            logger.info(f'Delete nginx conf file {file_path} success!')


extension = AppProxyNginxExtension()

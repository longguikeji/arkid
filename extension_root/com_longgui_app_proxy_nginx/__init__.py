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
import urllib
import requests


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
        logger.info(f"token:{token}, headers:{request.headers}")
        app = App.active_objects.filter(id=app_id).first()
        skip_token_verification = app.skip_token_verification
        if skip_token_verification:
            return 200, None
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
                app.url = f'{app_url}{urlparse(app.url).path}'

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
        # 只有平台租户可以设置proxy url
        tenant = event.tenant
        if not tenant.is_platform_tenant:
            return
        app = event.data
        nginx_app = NginxAPP.objects.filter(target=app).first()
        if not nginx_app:
            return

        frontend_url = get_app_config().get_frontend_host(schema=True)
        u = urlparse(frontend_url)
        app_server_name = f'{app.id.hex}.{u.hostname}'
        tenant_id = event.tenant.id.hex
        app_id = app.id.hex
        # port = 80
        #
        # 如果已经创建了nginx配置，is_intranet_url 为false，则删除该配置
        # 如果已经创建了配置，is_intranet_url为true，则返回什么也不做
        # 如果没有创建配置，is_intranet_url为true，则继续创建配置的逻辑
        if not nginx_app.is_intranet_url and nginx_app.nginx_config_created:
            logger.info("是否是内网地址变更为false，删除nginx配置")
            self.delete_nginx_conf(event)
            return
        elif nginx_app.is_intranet_url and nginx_app.nginx_config_created:
            logger.info("nginx配置已经创建过，不做处理")
            return
        elif nginx_app.is_intranet_url and not nginx_app.nginx_config_created:
            logger.info("开始创建nginx配置")

            # 判断app.url是否是http开头，并且可以连通的
            parsed_url = urlparse(app.url)
            if parsed_url.scheme != "http":
                logger.error(f"Wrong url Schema: {app.url}")
                return

            if not hasattr(app, "skip_verify_connection") or not getattr(
                app, "skip_verify_connection"
            ):
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/49.0.2')]
                try:
                    opener.open(app.url)
                except urllib.error.HTTPError:
                    logger.error('访问页面出错: {app.url}')
                    return
                except urllib.error.URLError:
                    logger.error('访问页面出错: {app.url}')
                    return

            arkid_be_host = os.environ.get("ARKIDBESVC")
            be_url = f'http://{arkid_be_host}/api/v1/tenant/{tenant_id}/com_longgui_app_proxy_nginx/nginx_auth/{app_id}'
            # portal_url = os.environ.get("ARKIDPORTALSVC")
            # if not portal_url:
            #     logger.info("没有配置ARKIDPORTALSVC环境变量")
            #     return
            try:
                # create_url = f"http://{portal_url}/create/nginxconf"
                u = urlparse(app.url)
                app_proxy_url = f"{u.scheme}://{u.netloc}"
                # json = {
                #     "dest_url": app_proxy_url,
                #     "server_name": app_server_name,
                #     "be_url": be_url,
                # }
                # res = requests.post(create_url, json=json)
                # if res.json().get('code') == 0:
                #     logger.info("Nginx 配置文件创建成功!")
                #     nginx_app.nginx_config_created = True
                #     nginx_app.save()
                # else:
                #     logger.info(f"Nginx 配置文件创建失败!: {res.text}")
                apisix_host = "apisix-admin:9180"
                apisix_key = "6f87ad84b625c8f1edd1c9f034335f13"
                headers = {
                    "X-API-KEY": apisix_key
                }
                route_url = f"{apisix_host}/apisix/admin/routes/{app.id.hex}"
                body = {
                    "uri": "/*",
                    "host": app_server_name,
                    "plugins": {
                        "forward-auth": {
                            "uri": be_url,
                            "request_headers": ["Cookie"],
                            # "upstream_headers": ["X-User-ID"],
                            # "client_headers": ["Location"]
                        }
                    },
                    "upstream": {
                        "nodes": {
                            app_proxy_url: 1
                        },
                        "type": "roundrobin"
                    }
                }
                logger.info(body)
                res = requests.put(route_url, json=body, headers=headers)
                if res.status_code == 201:
                    logger.info("apisix route更新成功!")
                    nginx_app.nginx_config_created = True
                    nginx_app.save()
                else:
                    logger.info(f"apisix route更新失败!: {res.status_code}-{res.text}")
            except Exception as e:
                logger.error("apisix创建更新route接口报错:")
                logger.error(e)
        logger.info("没有做任何处理")

    def delete_nginx_conf(self, event):
        app = event.data
        nginx_app = NginxAPP.objects.filter(target=app).first()
        if not nginx_app:
            return
        if not nginx_app.nginx_config_created:
            return

        logger.info("开始删除nginx配置")
        try:
            # portal_url = os.environ.get("ARKIDPORTALSVC")
            # if not portal_url:
            #     logger.info("没有配置ARKIDPORTALSVC环境变量")
            #     return
            # delete_url = f"http://{portal_url}/delete/nginxconf?appid={app.id.hex}"
            apisix_host = "apisix-admin:9180"
            apisix_key = "6f87ad84b625c8f1edd1c9f034335f13"
            headers = {
                "X-API-KEY": apisix_key
            }
            route_url = f"{apisix_host}/apisix/admin/routes/{app.id.hex}"
            res = requests.delete(route_url, headers=headers)
            if res.status_code == 200:
                logger.info("apisix 配置文件删除成功!")
                nginx_app.nginx_config_created = False
                nginx_app.nginx_config_deleted = True
                nginx_app.save()
            else:
                logger.info(f"apisix 配置文件删除失败!: {res.status_code}-{res.text}")

        except Exception as e:
            logger.error("portal删除配置接口报错:")
            logger.error(e)

extension = AppProxyNginxExtension()

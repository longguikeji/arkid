#!/usr/bin/env python3
import requests
from types import SimpleNamespace
from typing import Literal, Union
from ninja import Schema
from pydantic import Field
from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core import event as core_event
from arkid.extension.models import TenantExtensionConfig, TenantExtension
from arkid.core.extension import RootSchema, create_extension_schema
from pydantic import UUID4
from celery import shared_task
from arkid.common.logger import logger
from django.urls import reverse
from arkid.config import get_app_config
from scim_server.urls import urlpatterns as scim_server_urls
from django.urls import re_path
from scim_server.views.users_view import UsersViewTemplate
from scim_server.views.groups_view import GroupsViewTemplate
from scim_server.exceptions import NotImplementedException


class ExternalIdpExtension(Extension):
    TYPE = "external_idp"

    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'type'
    composite_model = TenantExtension

    @property
    def type(self):
        return ExternalIdpExtension.TYPE

    def load(self):
        # class UsersView(UsersViewTemplate):
        #     @property
        #     def provider(this):
        #         return self

        # class GroupsView(GroupsViewTemplate):
        #     @property
        #     def provider(this):
        #         return self

        # scim_server_urls = [
        #     re_path(
        #         rf'^scim/{self.name}/(?P<config_id>[\w-]+)/Users(?:/(?P<uuid>[^/]+))?$',
        #         UsersView.as_view(),
        #         name=f'{self.name}_scim_users',
        #     ),
        #     # re_path(r'^Groups/.search$', views.GroupSearchView.as_view(), name='groups-search'),
        #     re_path(
        #         rf'^scim/{self.name}/(?P<config_id>[\w-]+)/Groups(?:/(?P<uuid>[^/]+))?$',
        #         GroupsView.as_view(),
        #         name=f'{self.name}_scim_groups',
        #     ),
        # ]
        # self.register_routers(scim_server_urls, True)
        github_urls = [
            re_path(
                rf'^idp/{self.name}/(?P<settings_id>[\w-]+)/login$',
                self.login,
                name=f'{self.name}_login',
            ),
            # re_path(r'^Groups/.search$', views.GroupSearchView.as_view(), name='groups-search'),
            re_path(
                rf'^idp/{self.name}/(?P<settings_id>[\w-]+)/callback$',
                self.callback,
                name=f'{self.name}_callback',
            ),
            re_path(
                rf'^idp/{self.name}/(?P<settings_id>[\w-]+)/bind$',
                self.bind,
                name=f'{self.name}_bind',
            ),
        ]
        self.register_routers(github_urls, True)
        super().load()

    def login(self, request, settings_id):
        pass

    def callback(self, request, settings_id):
        pass

    def bind(self, request, settings_id):
        pass

    def get_img_url(self):
        pass

    def register_external_idp_schema(self, idp_type, schema):
        self.register_config_schema(schema, self.package + '_' + idp_type)
        self.register_composite_config_schema(
            schema, idp_type, exclude=['extension', 'settings']
        )

    def create_tenant_settings(self, tenant, settings, type):
        settings_created = super().create_tenant_settings(tenant, settings, type=type)
        server_host = get_app_config().get_host()
        package = self.package.replace('.', '_')
        login_url = server_host + reverse(
            f'{package}:{self.name}_login', args=[tenant.id, settings_created.id]
        )
        callback_url = server_host + reverse(
            f'{package}:{self.name}_callback',
            args=[tenant.id, settings_created.id],
        )
        bind_url = server_host + reverse(
            f'{package}:{self.name}_bind', args=[tenant.id, settings_created.id]
        )
        img_url = self.get_img_url()
        settings["login_url"] = login_url
        settings["callback_url"] = callback_url
        settings["bind_url"] = bind_url
        settings["img_url"] = img_url
        settings_created.settings = settings
        settings_created.save()
        return settings_created

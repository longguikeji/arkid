import asyncio
import requests
import datetime
import uuid
import collections
from django.db import models
from common.model import BaseModel
from app.models import App
from .constants import (
    ProvisioningMode,
    ProvisioningStatus,
    ProvisioningType,
    AuthenticationType,
)
from scim_client.async_client import AsyncSCIMClient
from aiohttp import BasicAuth, ClientSession
from scim2_filter_parser.attr_paths import AttrPath


class Config(BaseModel):

    STATUS_CHOICES = (
        (ProvisioningStatus.Enabled.value, 'Enabled'),
        (ProvisioningStatus.Disabled.value, 'Disabled'),
    )

    SYNC_TYPE = (
        (ProvisioningType.upstream.value, 'Upstream'),
        (ProvisioningType.downstream.value, 'Downstream'),
    )

    AUTH_TYPE = (
        (AuthenticationType.basic.value, 'Basic Auth'),
        (AuthenticationType.token.value, 'Token Auth'),
    )

    # MODE_CHOICES = ((ProvisioningMode.Automatic.value, 'Automatic'),)

    app = models.ForeignKey(App, on_delete=models.PROTECT)
    sync_type = models.IntegerField(
        max_length=32, choices=SYNC_TYPE, default=ProvisioningType.downstream.value
    )
    auth_type = models.IntegerField(
        max_length=32, choices=AUTH_TYPE, default=AuthenticationType.token.value
    )

    base_url = models.CharField(max_length=1024, blank=False, null=True)
    token = models.CharField(max_length=256, blank=True, null=True)

    # mode = models.IntegerField(choices=MODE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    username = models.CharField(max_length=256, blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)

    def should_provision_user(self, user):
        return True

    def should_provision_group(self, group):
        return True

    def get_scim_client(self, cookies=None):
        if self.auth_type == AuthenticationType.basic.value:
            basic_auth = BasicAuth(login=self.username, password=self.password)
            client = AsyncSCIMClient(
                '', base_url=self.base_url, auth=basic_auth, cookies=cookies
            )
        else:
            client = AsyncSCIMClient(
                self.token, base_url=self.base_url, cookies=cookies
            )
        return client

    def test_connection(self):
        client = self.get_scim_client()
        resp = asyncio.run(
            client.api_call(http_verb='GET', path='ServiceProviderConfig')
        )
        if resp.status_code != 200:
            return False
        else:
            return True

    def get_user_mapped_data(self, user):
        """
        {'name': {
                    'last_name': '',
                    'first_name': '',
                 },
         'emails': [{'value': 'xxx',
                     'type': 'work',
                     'primary': true,
                    }],
         'userName': 'test'
        }
        """
        # TODO 支持复杂类型的映射: emails[type eq "work"].value
        attr_map = {
            # attr, sub attr, uri
            ('externalId', None, None): 'scim_external_id',
            ('userName', None, None): 'username',
            ('name', 'familyName', None): 'last_name',
            ('familyName', None, None): 'last_name',
            ('name', 'givenName', None): 'first_name',
            ('givenName', None, None): 'first_name',
            ('active', None, None): 'is_active',
            ('nickName', None, None): 'nickname',
            ('title', None, None): 'job_title',
            ('emails', 'type', None): 'email',
            ('emails', 'value', None): 'email',
            ('phoneNumbers', 'value', None): 'mobile',
            ('phoneNumbers', 'type', None): 'mobile',
        }
        data = {}
        mappings = self.app_profile_mappings.all()
        if not mappings:
            return {}
        for mp in mappings:
            value = getattr(user, mp.source_attribute)
            if not value:
                continue
            else:
                # data[mp.target_attribute] = value
                path = mp.target_attribute
                filter_ = path + ' eq "{}"'.format(value)
                attr_path = AttrPath(filter_, attr_map)
                if not list(attr_path):
                    print('No attribute path found in request')
                    continue
                if attr_path.is_complex:
                    attr, sub_attr, uri = attr_path.first_path
                    attr_name = attr if not uri else f'{uri}:{attr}'
                    if attr_name in data and isinstance(data[attr_name], list):
                        value_list = data[attr_name]
                    else:
                        data[attr_name] = []
                        value_list = data[attr_name]

                    d = {}
                    for p, value in attr_path.params_by_attr_paths.items():
                        attr, sub_attr, uri = p
                        d[sub_attr] = value
                    value_list.append(d)
                else:
                    attr, sub_attr, uri = attr_path.first_path
                    attr_name = attr if not uri else f'{uri}:{attr}'
                    if not sub_attr:
                        data[attr_name] = value
                    else:
                        if attr_name in data and isinstance(data[attr_name], dict):
                            data[attr_name][sub_attr] = value
                        else:
                            data[attr_name] = {sub_attr: value}
        return data

    def get_match_filter(self, user):
        """
        filter=userName eq "bjensen"
        filter=name.familyName co "O'Malley"
        filter=emails[type eq "work" and value co "@example.com"]
        emails[type eq "work"].value eq "@examples.com"
        """
        match_mappings = self.app_profile_mappings.filter(
            is_used_matching=True
        ).order_by('matching_precedence')
        if not match_mappings:
            return '''userName eq "{}"'''.format(user.username)
        filter_str_list = []
        for mm in match_mappings:
            value = getattr(user, mm.source_attribute)
            if not value:
                continue
            filter_str = '''{} eq "{}"'''.format(mm.target_attribute, value)
            filter_str_list.append(filter_str)

        if filter_str_list:
            return " or ".join(filter_str_list)
        else:
            return '''userName eq "{}"'''.format(user.username)

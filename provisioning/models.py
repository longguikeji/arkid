import asyncio
import requests
import datetime
import uuid
import collections
from django.db import models
from common.model import BaseModel
from app.models import App
from .constants import ProvisioningMode, ProvisioningStatus, ProvisioningType, AuthenticationType
from scim2_client.scim_service import ScimService
from scim_client.async_client import AsyncSCIMClient
from aiohttp import BasicAuth, ClientSession


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
    sync_type = models.CharField(max_length=32, choices=SYNC_TYPE, default=ProvisioningType.downstream.value)
    auth_type = models.CharField(max_length=32, choices=AUTH_TYPE, default=AuthenticationType.token.value)

    base_url = models.CharField(max_length=1024, blank=False, null=True)
    token = models.CharField(max_length=256, blank=True, null=True)

    # mode = models.IntegerField(choices=MODE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    username = models.CharField(max_length=256, blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)

    def should_provision(self, user):
        return True

    def get_scim_client(self, cookies=None):
        if self.auth_type == AuthenticationType.basic.value:
            basic_auth = BasicAuth(login=self.username, password=self.password)
            client = AsyncSCIMClient(base_url=self.base_url, auth=basic_auth, cookies=cookies)
        else:
            client = AsyncSCIMClient(base_url=self.base_url, token=self.token, cookies=cookies)
        return client

    def test_connection(self):

        client = self.get_scim_client()
        resp = asyncio.run(client.api_call(http_verb='GET', path='ServiceProviderConfig'))
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
        data = {}
        mappings = self.app_profile_mappings.all()
        if not mappings:
            return {}
        for mp in mappings:
            value = getattr(user, mp.source_attribute)
            if not value:
                continue
            else:
                data[mp.target_attribute] = value
        return data

    def get_match_filter(self, user):
        """
        filter=userName eq "bjensen"
        filter=name.familyName co "O'Malley"
        filter=emails[type eq "work" and value co "@example.com"]
        emails[type eq "work"].value eq "@examples.com"
        """
        match_mappings = self.app_profile_mappings.filter(is_used_matching=True).order_by(
            'matching_precedence'
        )
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

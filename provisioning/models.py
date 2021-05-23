import requests
import datetime
import uuid
import collections
from django.db import models
from common.model import BaseModel
from app.models import App
from schema.models import Schema
from .constants import ProvisioningMode, ProvisioningStatus
from scim2_client.scim_service import ScimService

TargetAttr = collections.namedtuple(
    'TargetAttr',
    [
        'name',
        'scim_path',
        'sub_attrs',
        'mapping_type',
        'constant_value',
        'default_value_if_is_none',
        'is_used_matching',
        'matching_precedence',
    ],
)

DEFAULT_MAPPING = {
    'username': TargetAttr('userName', 'userName', {}, 1, '', '', True, -1),
    'first_name': TargetAttr('givenName', 'name.givenName', {}, 1, '', '', False, -1),
    'last_name': TargetAttr('familyName', 'name.familyName', {}, 1, '', '', False, -1),
    'email': TargetAttr(
        'email', 'emails', {'primary': True, 'type': 'work'}, 1, '', '', False, -1
    ),
}


class Config(BaseModel):

    STATUS_CHOICES = (
        (ProvisioningStatus.Enabled.value, 'Enabled'),
        (ProvisioningStatus.Disabled.value, 'Disabled'),
    )

    MODE_CHOICES = ((ProvisioningMode.Automatic.value, 'Automatic'),)

    app = models.ForeignKey(App, on_delete=models.PROTECT)
    endpoint = models.CharField(max_length=1024, blank=False, null=True)
    token = models.CharField(max_length=256, blank=True, null=True)
    schemas = models.ManyToManyField(Schema, blank=True)

    mode = models.IntegerField(choices=MODE_CHOICES, default=0)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1)

    username = models.CharField(max_length=256, blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)

    def should_provision(self, user):
        return True

    def get_basic_auth_session(self):
        s = requests.Session()
        try:
            URL1 = 'http://localhost:9000/superadmin/'
            URL2 = 'http://localhost:9000/superadmin/login/?next=/superadmin/'

            # Retrieve the CSRF token first
            s.get(URL1)  # sets the cookie
            csrftoken = s.cookies['csrftoken']

            data = dict(
                username=self.username,
                password=self.password,
                csrfmiddlewaretoken=csrftoken,
            )
            headers = {'Referer': 'foo'}
            r = s.post(URL2, data=data, headers=headers)
            return s
        except Exception as e:
            print(e)
            return None

    def get_token_auth_session(self):
        s = requests.Session()
        token = 'Bearer {}'.format(self.token)
        s.headers.update({'Authorization': token})
        return s

    def get_session(self):
        if self.token:
            return self.get_token_auth_session()
        elif self.username and self.password:
            return self.get_basic_auth_session()
        else:
            return None

    def ensure_connection(self):
        s = self.get_session()
        if not s:
            return False

        from .utils import user_exists, create_user, delete_user, list_users

        from inventory.models import User

        service = ScimService(s, self.endpoint)
        username = 'test-{}'.format(uuid.uuid4().hex)
        user = User(username=username)
        ret = False
        if not user_exists(service, self, user):
            user_id = create_user(service, self, user)
            if user_id:
                ret = delete_user(service, self, user_id)
        else:
            ret = delete_user(service, self, user)
        return ret

        # test list_users

        # list_users(service, self)

    def parse_schemas(self):
        mapping = {}
        for sch in self.schemas.all():
            target_attr = TargetAttr(
                sch.target_attribute,
                sch.scim_path,
                sch.sub_attrs,
                sch.mapping_type,
                sch.constant_value,
                sch.default_value_if_is_none,
                sch.is_used_matching,
                sch.matching_precedence,
            )
            mapping[sch.source_attribute] = target_attr
        return mapping

    def persist_default_mapping(self):
        for src_attr, target_attr in DEFAULT_MAPPING.items():
            sch = Schema.objects.create(
                name=src_attr,
                source_attribute=src_attr,
                target_attribute=target_attr.name,
                scim_path=target_attr.scim_path,
                sub_attrs=target_attr.sub_attrs,
                mapping_type=target_attr.mapping_type,
                constant_value=target_attr.consant_value,
                default_value_if_is_none=target_attr.default_value_if_is_none,
                is_used_matching=target_attr.is_used_matching,
                matching_precedence=target_attr.matching_precedence,
            )
            self.schemas.add(sch)

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
        schemas = self.schemas.all()
        if not schemas:
            mapping = DEFAULT_MAPPING
            # self.persist_default_mapping()
        else:
            mapping = self.parse_schemas()
        data = {}
        for key, target_attr in mapping.items():
            mapping_type = target_attr.mapping_type

            if mapping_type == '0':  # None
                continue
            elif mapping_type == 1:  # Direct
                value = getattr(user, key)
            elif mapping_type == 2:  # Constant
                value = target_attr.constant_value
            elif mapping_type == 3:  # Expression
                continue

            if not value:
                continue
            scim_path = target_attr.scim_path
            sub_paths = scim_path.split('.')
            prev = data
            for i in range(len(sub_paths) - 1):
                path = sub_paths[i]
                prev[path] = prev.get(path) or {}
                prev = prev[path]
            if target_attr.sub_attrs:
                prev[sub_paths[-1]] = [dict(value=value, **target_attr.sub_attrs)]
            else:
                name = sub_paths[-1]
                prev[name] = value
        return data

    def get_filter_str(self, user):
        """
        filter=userName eq "bjensen"
        filter=name.familyName co "O'Malley"
        filter=emails[type eq "work" and value co "@example.com"]
        emails[type eq "work" and value co "@example.com"]
        """
        match_attrs = self.schemas.filter(is_used_matching=True).order_by(
            'matching_precedence'
        )
        if not match_attrs:
            filter_str = 'userName eq "{}"'.format(user.username)
            return filter_str
        for attr in match_attrs:
            value = getattr(user, attr.source_attribute)
            if not value:
                continue
            if attr.sub_attrs:
                temp_str = []
                for key, val in attr.sub_attrs.items():
                    temp_str.append('{} eq "{}"'.format(key, val))
                temp_str.append('value eq "{}"'.format(value))
                filter_str = '{}[{}]'.format(attr.scim_path, ' and '.join(temp_str))
                yield filter_str
            else:
                filter_str = '{} eq "{}"'.format(attr.scim_path, value)
                yield filter_str

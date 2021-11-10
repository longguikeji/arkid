import json
from typing import Dict
from common.provider import LoginRegisterConfigProvider
from .form import LdapLoginForm
from common.code import Code
from django.utils.translation import gettext_lazy as _
from inventory.models import User

from .ldap import LdapAuth


class LdapLoginConfigProvider(LoginRegisterConfigProvider):
    def __init__(self, data=None, request=None, tenant=None) -> None:
        self.login_enabled = data.get('login_enabled', True)
        self.request = request
        self.tenant = tenant
        self.host = data.get("host")
        self.port = data.get("port")
        self.bind_dn = data.get("bind_dn")
        self.bind_password = data.get("bind_password")
        self.user_search_base = data.get("user_search_base")
        self.user_object_class = data.get("user_object_class")
        self.username_attr = data.get("username_attr")
        self.user_attr_map = json.loads(data.get("user_attr_map"))
        self.use_tls = data.get("use_tls")

    @property
    def login_form(self):
        if self.login_enabled:
            return LdapLoginForm(self).get_form()
        return None

    def authenticate(self, request):
        ''' '''
        username = request.data.get('username')
        password = request.data.get('password')
        user, err_msg = self._get_login_user(username, password)
        if not user:
            data = {
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            }
            return data

        data = {
            'error': Code.OK.value,
            'user': user,
        }
        return data

    def _get_login_user(self, username, password):
        settings = {
            "host": self.host,
            "port": self.port,
            "bind_dn": self.bind_dn,
            "bind_password": self.bind_password,
            "user_search_base": self.user_search_base,
            "user_object_class": self.user_object_class,
            "username_attr": self.username_attr,
            "use_tls": self.use_tls,
        }
        auth = LdapAuth(**settings)
        ladp_user_attrs, err_msg = auth.authenticate(username=username, password=password)
        if not ladp_user_attrs:
            return None, err_msg

        user_attrs = {}
        for k, v in self.user_attr_map.items():
            if v in ladp_user_attrs:
                user_attrs[k] = ladp_user_attrs[v]

        # Update or create the user.
        user, created = User.objects.update_or_create(**user_attrs)
        # If the user was created, set them an unusable password.
        if created:
            user.set_unusable_password()
            if self.tenant:
                user.tenants.add(self.tenant)
            user.save()

        return user, None

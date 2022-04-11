from typing import Dict
from common.provider import LoginRegisterConfigProvider
from common import loginpage as lp
from .constants import KEY
from django.urls import reverse
from config import get_app_config
from common.native_field import NativeFieldNames
from inventory.models import CustomField, Group, User, UserPassword, CustomUser
from tenant.models import Tenant, TenantConfig
from system.models import SystemConfig
from common.utils import (
    get_client_ip,
    check_password_complexity,
    set_user_register_count,
    get_user_register_count,
    get_password_error_count,
    get_request_tenant,
)
from rest_framework.exceptions import ValidationError

from .form import PasswordLoginForm, PasswordRegisterForm
from common.exception import ValidationFailed
from common.code import Code
from django.utils.translation import gettext_lazy as _
import datetime
from django.utils import timezone


class PasswordLoginRegisterConfigProvider(LoginRegisterConfigProvider):
    def __init__(self, data=None, request=None, tenant=None) -> None:
        self.login_enabled = data.get('login_enabled', True)
        self.register_enabled = data.get('register_enabled', True)
        self.login_enabled_field_names = data.get('login_enabled_field_names', ["username"])
        self.register_enabled_field_names = data.get('register_enabled_field_names', ["username"])
        self.password_validity_period = data.get('password_validity_period', 0)
        # self.is_open_authcode = data.get('is_open_authcode', False)
        # self.error_number_open_authcode = data.get('error_number_open_authcode', 0)
        self.request = request
        self.tenant = tenant

    @property
    def login_form(self):
        if self.login_enabled and self.login_enabled_field_names:
            return PasswordLoginForm(self).get_form()
        return None

    @property
    def register_form(self):
        forms = []
        if self.register_enabled and self.register_enabled_field_names:
            for name in self.register_enabled_field_names:
                if name == 'username':
                    forms.append(PasswordRegisterForm(self, name, '用户名').get_form())
                else:
                    forms.append(PasswordRegisterForm(self, name, name).get_form())
        return forms

    def _get_password_validity_period(self, request):
        tenant = get_request_tenant(request)
        config = None
        if tenant:
            config = TenantConfig.valid_objects.filter(tenant=tenant).first()
        else:
            config = SystemConfig.valid_objects.filter().first()
        if not config:
            return None
        else:
            return config.data.get('password_validity_period', None)

    def authenticate(self, request):
        ''' '''

        username = request.data.get('username')
        password = request.data.get('password')
        user = self._get_login_user(username)
        if not user or not user.check_password(password):
            data = {
                'error': Code.USERNAME_PASSWORD_MISMATCH.value,
                'message': _('username or password is not correct'),
            }

            return data

        # check password validity
        # now = datetime.datetime.now()
        now = timezone.now()
        last_update_pwd = user.last_update_pwd
        if last_update_pwd:
            if self.password_validity_period:
                interval = now - last_update_pwd
                if interval.days >= self.password_validity_period:
                    return {
                        'error': Code.PASSWORD_EXPIRED_ERROR.value,
                        'message': _('password expired, please reset password'),
                        'user': user
                    }

        data = {
            'error': Code.OK.value,
            'user': user,
        }
        return data

    def register_user(self, request):
        tenant = get_request_tenant(request)
        password = request.data.get('password')
        ret, message = check_password_complexity(password, tenant)
        if not ret:
            data = {
                'error': Code.PASSWORD_STRENGTH_ERROR.value,
                'message': message,
            }
            return data

        if 'username' in request.data:
            field_name = 'username'
        elif 'email' in request.data:
            field_name = 'email'
        else:
            for key in request.data:
                if key not in ('password', 'checkpassword'):
                    field_name = key
                    break

        field_value = request.data.get(field_name)
        user = self._get_register_user(field_name, field_value)
        if user:
            data = {
                'error': Code.USERNAME_EXISTS_ERROR.value,
                'message': _('username already exists'),
            }
            return data
        # username字段也填入默认值
        if field_name in ('username', 'email'):
            kwargs = {field_name: field_value}
            if field_name == 'email':
                kwargs.update(username=field_value)
            user = User.objects.create(
                is_del=False,
                is_active=True,
                **kwargs,
            )
        else:
            user = User.objects.create(
                is_del=False,
                is_active=True,
                username=field_value,
            )
            CustomUser.objects.create(user=user, data={field_name: field_value})

        user.set_password(password)
        user.save()
        data = {'error': Code.OK.value, 'user': user}
        return data

    def _get_login_user(self, username):
        user = None
        if 'username' in self.login_enabled_field_names:
            user = User.active_objects.filter(username=username).first()
            self.login_enabled_field_names.remove('username')
        if not user and 'email' in self.login_enabled_field_names:
            user = User.active_objects.filter(email=username).first()
            self.login_enabled_field_names.remove('email')
        if not user and self.login_enabled_field_names:

            # 自定义字段查找用户
            for name in self.login_enabled_field_names:
                custom_field = CustomField.valid_objects.filter(
                    name=name, subject='user'
                )
                if not custom_field:
                    continue
                custom_user = CustomUser.valid_objects.filter(
                    data__name=username
                ).first()
                if custom_user:
                    user = custom_user.user
        return user

    def _get_register_user(self, field_name, field_value):
        user = None
        if field_name in ('username', 'email'):
            user = User.active_objects.filter(**{field_name: field_value}).first()
        else:
            custom_field = CustomField.valid_objects.filter(
                name=field_name, subject='user'
            )
            if not custom_field:
                return None

            custom_user = CustomUser.valid_objects.filter(data__name=field_name).first()
            if custom_user:
                user = custom_user.user
        return user

import re
from arkid.core.extension import AuthFactorExtension
from arkid.core.error import ErrorCode
from arkid.core.translation import gettext_default as _
from .models import UserPassword
from ninja import ModelSchema
from typing import Literal, Union

class PasswordAuthFactorSchema(ModelSchema):
    package: Literal['cat']
    class Config:
        model = UserPassword
        model_fields = "__all__"

class PasswordAuthFactorSchema2(ModelSchema):
    package: Literal['dog']
    class Config:
        model = UserPassword
        model_fields = "__all__"

class PasswordAuthFactorExtension(AuthFactorExtension):
    def load(self):
        super().load()
        self.register_extend_field(UserPassword, "password")
        # self.register_config_schema(PasswordAuthFactorSchema)
        # self.register_config_schema(PasswordAuthFactorSchema2)

    def authenticate(self, event, **kwargs):
        print(**kwargs)
        tenant = event.tenant
        request = event.data.request
        username = request.POST.get('username')
        password = request.POST.get('password')

    def register(self, event, **kwargs):
        tenant = event.tenant
        request = event.request
        username = request.POST.get('username')
        password = request.POST.get('password')
        config = self.get_current_config(event)
        ret, message = self.check_password_complexity(password, config)
        if not ret:
            data = {
                'error': ErrorCode.PASSWORD_STRENGTH_ERROR.value,
                'message': message,
            }
            return data

        if 'username' in request.POST:
            field_name = 'username'
        elif 'email' in request.POST:
            field_name = 'email'
        else:
            for key in request.POST:
                if key not in ('password', 'checkpassword'):
                    field_name = key
                    break

        field_value = request.POST.get(field_name)
        user = self._get_register_user(field_name, field_value)
        if user:
            data = {
                'error': ErrorCode.USERNAME_EXISTS_ERROR.value,
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
        data = {'error': ErrorCode.OK.value, 'user': user}
        return data

    def reset_password(self, event, **kwargs):
        pass

    def create_login_page(self, event, config):
        pass

    def create_register_page(self, event, config):
        pass

    def create_password_page(self, event, config):
        pass

    def create_other_page(self, event, config):
        pass
    
    def check_password_complexity(self, pwd, config):
        if not pwd:
            return False, 'No password provide'

        if config:
            regular = config.config.get('regular')
            title = config.config.get('title')
            if re.match(regular, pwd):
                return True, None
            else:
                return False, title
        return True, None

    def _get_register_user(self, field_name, field_value):
        # user = None
        # if field_name in ('username', 'email'):
        #     user = .active_objects.filter(**{field_name: field_value}).first()
        # else:
        #     custom_field = CustomField.valid_objects.filter(
        #         name=field_name, subject='user'
        #     )
        #     if not custom_field:
        #         return None

        #     custom_user = CustomUser.valid_objects.filter(data__name=field_name).first()
        #     if custom_user:
        #         user = custom_user.user
        # return user
        pass

extension = PasswordAuthFactorExtension(
    package="com.longgui.password_auth_factor",
    description="Password 认证因素",
    version='1.0',
    labels='auth_factor',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)
import logging

import django
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from arkid.core.models import User


logger = logging.getLogger(__name__)


class LoginForm(forms.Form):
    """Standard username and password authentication form."""
    username = forms.CharField(label=_("Username"),
                               error_messages={'required':
                                               _("Please enter your username")})
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput,
                               error_messages={'required':
                                               _("Please enter your password")})

    if django.VERSION >= (1, 9):
        password.strip = False

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm, self).__init__(*args, **kwargs)
        if getattr(settings, 'MAMA_CAS_ALLOW_AUTH_WARN', False):
            self.fields['warn'] = forms.BooleanField(
                    widget=forms.CheckboxInput(),
                    label=_("Warn before automatic login to other services"),
                    required=False)

    def clean(self):
        """
        Pass the provided username and password to the active
        authentication backends and verify the user account is
        not disabled. If authentication succeeds, the ``User`` object
        is assigned to the form so it can be accessed in the view.
        """
        from django.contrib.auth.hashers import check_password
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        tenant_id = self.request.tenant_id
        # try:
        #     self.user = authenticate(request=self.request, username=username, password=password)
        # except Exception:
        #     logger.exception("Error authenticating %s" % username)
        #     error_msg = _('Internal error while authenticating user')
        #     raise forms.ValidationError(error_msg)
        if username and password:
            users = User.expand_objects.filter(tenant_id=tenant_id, username=username)
            if len(users) > 1:
                logger.warning("Failed authentication for %s" % username)
                error_msg = _('The username have many users')
                raise forms.ValidationError(error_msg)
            user = users[0] if users else None
            if user:
                user_password = user.get("password")
                if user_password and check_password(password, user_password):
                    user = User.active_objects.get(id=user.get("id"))
            # 进一步赋值
            self.user = user
            # 如果用户名密码错误的话就返回
            if self.user is None:
                logger.warning("Failed authentication for %s" % username)
                error_msg = _('The username or password is not correct')
                raise forms.ValidationError(error_msg)
            else:
                if not self.user.is_active:
                    logger.warning("User account %s is disabled" % username)
                    error_msg = _('This user account is disabled')
                    raise forms.ValidationError(error_msg)

        return self.cleaned_data


class LoginFormEmail(LoginForm):
    """
    Subclass of ``LoginForm`` that extracts the username if an email
    address is provided.
    """
    def clean_username(self):
        """
        Remove an '@<domain>' suffix if present and return only
        the username.
        """
        username = self.cleaned_data.get('username').split('@')[0]
        if not username:
            raise forms.ValidationError(_('Invalid username provided'))
        return username

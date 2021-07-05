from django.conf import settings
from django.contrib.auth import logout, REDIRECT_FIELD_NAME
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http.response import HttpResponseRedirect

class AccessMixin:
    """
    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = None
    permission_denied_message = ''
    raise_exception = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_login_url(self):
        """
        Override this method to override the login_url attribute.
        """
        login_url = self.login_url or settings.SAML_LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute. Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__))
        return str(login_url)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message attribute.
        """
        return self.permission_denied_message

    def get_redirect_field_name(self):
        """
        Override this method to override the redirect_field_name attribute.
        """
        return self.redirect_field_name

    def handle_no_permission(self, request_data):
        '''
        未登录用户跳转登录页面
        '''
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return HttpResponseRedirect(settings.SAML_LOGIN_URL + '?SAMLRequest={}'.format(request_data))


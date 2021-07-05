from .AccessMixin import AccessMixin


class LoginRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated."""

    def dispatch(self, request, *args, **kwargs):
        '''检查用户cookies是否登录
        '''
        try:
            spauthn = request.COOKIES['spauthn']
            token = ExpiringToken.objects.get(key=spauthn)
            exp = token.expired()
            if not exp:
                return super().dispatch(request, *args, **kwargs)
        except Exception:    # pylint: disable=broad-except
            return self.handle_no_permission(request.session['SAMLRequest'])

"""Utility views for Expiring Tokens.

Classes:
    ObtainExpiringAuthToken: View to provide tokens to clients.
"""
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from drf_expiring_authtoken.models import ExpiringToken
from drf_expiring_authtoken.serializers import AuthTokenSerializer
from executer.log.rdb import LOG_CLI


class IsAuthenticatedExceptPost(IsAuthenticated):
    def has_permission(self, request, view):
        res = request.method == "POST" \
            or super().has_permission(request, view)
        return res


class ObtainExpiringAuthToken(ObtainAuthToken):
    """View enabling username/password exchange for expiring token."""

    model = ExpiringToken

    permission_classes = [IsAuthenticatedExceptPost]
    authentication_classes = []

    def delete(self, request):
        ExpiringToken.objects.filter(user=request.user).delete()
        return Response(status=HTTP_204_NO_CONTENT)

    def post(self, request, *args, **kwargs):
        """Respond to POSTed username/password with token."""
        serializer = AuthTokenSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            res = self.pre_get_token(request)
            if res:
                return res
            user = serializer.validated_data['user']
            token, _ = ExpiringToken.objects.get_or_create(user=user)
            if token.expired():
                # If the token is expired, generate a new one.
                token.delete()
                token = ExpiringToken.objects.create(user=user)

            data = {'token': token.key, **self.attachment(token)}
            LOG_CLI(user).user_login()
            user.update_last_active_time()
            response = Response(data)
            response.set_cookie('spauthn', token.key)
            return response

        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def attachment(self, token):
        '''
        :rtype: dict
        '''
        return {}

    def pre_get_token(self, request):
        '''
        hook before get token
        '''
        return None


obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()

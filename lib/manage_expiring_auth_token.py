from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication
from rest_framework_expiring_authtoken.views import ObtainExpiringAuthToken
from rest_framework_expiring_authtoken.models import ExpiringToken


class IsAuthenticatedExceptPost(IsAuthenticated):
    def has_permission(self, request, view):
        return request.method == "POST" \
            or super().has_permission(request, view)


class ManageExpiringAuthToken(ObtainExpiringAuthToken):
    """
    Extend ObtainExpiringAuthToken to providing deleting token function.
    """
    permission_classes = [IsAuthenticatedExceptPost]
    authentication_classes = [ExpiringTokenAuthentication]

    def delete(self, request):
        ExpiringToken.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
from ninja.security import HttpBearer
from arkid.core.models import ExpiringToken

class AuthBearer(HttpBearer):

    def authenticate(self, request, token):
        expiring_token = ExpiringToken.objects.filter(token=token).first()
        if expiring_token:
            if expiring_token.expired(request.tenant) is False:
                return True
        return False
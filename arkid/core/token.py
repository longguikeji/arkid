import os
import binascii


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def refresh_token(user):
    from arkid.core.models import ExpiringToken
    token, _ = ExpiringToken.objects.update_or_create(user=user, defaults={"token": generate_token()})
    return token.token

def get_valid_token(user, tenant):
    '''
    如果没过期就不刷新，过期才刷新
    '''
    from arkid.core.models import ExpiringToken
    token = ExpiringToken.objects.filter(user=user).first()
    if token and not token.expired:
        return token.token
    token = refresh_token(user)
    return token
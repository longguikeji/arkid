import os
import binascii


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def refresh_token(user):
    from arkid.core.models import ExpiringToken
    token, _ = ExpiringToken.objects.update_or_create(user=user, defaults={"token": generate_token()})
    return token.token

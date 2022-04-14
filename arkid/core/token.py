from arkid.core.models import ExpiringToken


def refresh_token(user):
    token, created = ExpiringToken.objects.get_or_create(user=user)
    if not created:
        token = token.refresh_token()
    user_token = token.token
    return user_token

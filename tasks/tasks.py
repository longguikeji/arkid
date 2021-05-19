from common.event import Event
import typing
from .celery import app
from app.models import App
from django.db.models import QuerySet
from provisioning.models import Config
from provisioning.constants import ProvisioningStatus
from provisioning.utils import create_user, user_exists, update_user
from inventory.models import User, Group
from app.models import App
from webhook.models import WebHook, WebHookTriggerHistory
import requests


@app.task
def provision_user(tenant_uuid: str, user_id: int):
    apps = App.active_objects.filter(
        tenant__uuid=tenant_uuid,
    )

    for app in apps:
        config: Config = Config.active_objects.filter(
            app=app,
        ).first()

        if config is None or config.status != ProvisioningStatus.Enabled.value:
            continue

        provision_app_user.delay(tenant_uuid, app.id, config.id, user_id)


@app.task
def provision_app_user(tenant_uuid: str, app_id: int, config_id: int, user_id: int):
    print(
        f'task: provision_app_user, tenant: {tenant_uuid}, app: {app_id}, user: {user_id}'
    )

    # TODO: check the scope of the selected range
    user: User = User.objects.get(id=user_id)
    config: Config = Config.objects.get(id=config_id)
    if not config.should_provision(user):
        print(f'User Provisioning Skiped: {user_id}')
        return

    if not user_exists(config, user):
        create_user(config, user)
    else:
        update_user(user)


@app.task
def notify_webhook(tenant_uuid: int, event: Event):
    webhooks = WebHook.objects.filter(
        tenant__uuid=tenant_uuid,
    )

    webhook: WebHook
    for webhook in webhooks:
        r = requests.post(webhook.url)
        print(r.json())

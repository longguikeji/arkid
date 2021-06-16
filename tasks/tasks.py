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
from scim2_client.scim_service import ScimService
from provisioning.constants import ProvisioningType


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
        # 只支持下游同步
        if config.sync_type == ProvisioningType.upstream.value:
            continue

        # provision_app_user.delay(tenant_uuid, app.id, config.id, user_id)
        provision_app_user(tenant_uuid, app.id, config.id, user_id)


@app.task
def provision_app_user(tenant_uuid: str, app_id: int, config_id: int, user_id: int):
    """
    同步逻辑：
    根据profile mapping的match attributes判断APP有没有该User,如果不存在,
    直接Create, 如果存在, 更新该User的属性

    """
    print(
        f'task: provision_app_user, tenant: {tenant_uuid}, app: {app_id}, user: {user_id}'
    )

    # TODO: check the scope of the selected range
    user: User = User.objects.get(id=user_id)
    config: Config = Config.objects.get(id=config_id)
    if not config.should_provision(user):
        print(f'User Provisioning Skiped: {user_id}')
        return

    # cookies = {'sessionid': 'iidk5ugp4myow9jzt4sxb5g8eb5hf3gs'}
    scim_client = config.get_scim_client()
    is_exist = user_exists(scim_client, config, user)
    if not is_exist:
        user_id = create_user(scim_client, config, user)
        print('created user with uuid: {}'.format(user_id))
    else:
        update_user(scim_client, config, user, user_id)



@app.task
def notify_webhook(tenant_uuid: int, event: Event):
    webhooks = WebHook.objects.filter(
        tenant__uuid=tenant_uuid,
    )

    webhook: WebHook
    for webhook in webhooks:
        r = requests.post(webhook.url)
        print(r.json())

@app.task
def provision_tenant_app(tenant_uuid: str, app_id:int):
    pass

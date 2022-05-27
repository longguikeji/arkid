#!/usr/bin/env python3

from typing import List
from pydantic import Field
from ninja import Schema, ModelSchema
from arkid.core.translation import gettext_default as _
from arkid.core.schema import ResponseSchema
from webhook.models import Webhook, WebhookEvent, WebhookTriggerHistory
from arkid.core import pages, actions

select_events_page = pages.TablePage(select=True, name=_("Select Events", "选择事件"))

pages.register_front_pages(select_events_page)

select_events_page.create_actions(
    init_action=actions.DirectAction(
        path='/api/v1/tenant/{tenant_id}/event_list/',
        method=actions.FrontActionMethod.GET,
    ),
    # node_actions=[
    #     actions.DirectAction(
    #         path='/api/v1/tenant/{tenant_id}/app_groups/?parent_id={id}',
    #         method=actions.FrontActionMethod.GET,
    #     )
    # ],
)


class WebhookListItemOut(ModelSchema):
    class Config:
        model = Webhook
        model_fields = ['id', 'name', 'url', 'secret']

    events: List[str]

    @staticmethod
    def resolve_events(obj):
        events = []
        for e in obj.events_set.all():
            events.append(e.event_type)
        return events


class WebhookListOut(ResponseSchema):
    data: List[WebhookListItemOut]


class WebhookSchema(Schema):
    name: str = Field(title=_('Name', '名称'), default='')
    url: str = Field(title=_('Url', '应用URL'))
    secret: str = Field(title=_('Secret', '签名密钥'), defaut='')
    events: List[str] = Field(
        title=_('Events', '监听事件'),
        field="tag",
        page=select_events_page.tag,
        link="name",
        type="array",
    )


class WebhookOut(ResponseSchema):
    data: WebhookSchema


class WebhookCreateIn(WebhookSchema):
    pass


class WebhookCreateOut(ResponseSchema):
    pass


class WebhookUpdateIn(WebhookSchema):
    data: WebhookSchema


class WebhookUpdateOut(ResponseSchema):
    pass


class WebhookDeleteOut(ResponseSchema):
    pass


class WebhookHistoryListItemOut(ModelSchema):
    class Config:
        model = WebhookTriggerHistory
        model_fields = ['id', 'status', 'request', 'response']


class WebhookHistoryListOut(ResponseSchema):
    data: List[WebhookHistoryListItemOut]


class WebhookHistoryOut(ResponseSchema):
    data: WebhookHistoryListItemOut


class WebhookHistoryRetryOut(ResponseSchema):
    pass


class WebhookHistoryDeleteOut(ResponseSchema):
    pass

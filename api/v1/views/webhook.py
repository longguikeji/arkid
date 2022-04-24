from arkid.core.api import api
from arkid.core.translation import gettext_default as _


@api.get("/tenant/{tenant_id}/webhooks/", tags=[_("Webhook")])
def get_webhooks(request, tenant_id: str):
    """ Webhook列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/webhooks/{id}/", tags=[_("Webhook")])
def get_webhook(request, tenant_id: str, id: str):
    """ 获取Webhook,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/webhooks/", tags=[_("Webhook")])
def create_webhook(request, tenant_id: str):
    """ 创建Webhook,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/webhooks/{id}/", tags=[_("Webhook")])
def update_webhook(request, tenant_id: str, id: str):
    """ 编辑Webhook,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/webhooks/{id}/", tags=[_("Webhook")])
def delete_webhook(request, tenant_id: str, id: str):
    """ 删除Webhook,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/webhooks/{webhook_id}/histories/", tags=[_("Webhook")])
def get_webhook_histories(request, tenant_id: str, webhook_id: str):
    """ 获取Webhook历史记录列表,TODO
    """
    return []

@api.get("/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/", tags=[_("Webhook")])
def get_webhook_history(request, tenant_id: str, webhook_id: str, id:str):
    """ 获取Webhook历史记录,TODO
    """
    return {}

@api.post("/tenant/{tenant_id}/webhooks/{webhook_id}/histories/", tags=[_("Webhook")])
def create_webhook_history(request, tenant_id: str, webhook_id: str):
    """ 创建Webhook历史记录,TODO
    """
    return {}

@api.put("/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/", tags=[_("Webhook")])
def update_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """ 编辑Webhook历史记录,TODO
    """
    return {}

@api.delete("/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/", tags=[_("Webhook")])
def delete_webhook_history(request, tenant_id: str, webhook_id: str, id: str):
    """ 删除Webhook历史记录,TODO
    """
    return {}

@api.get("/tenant/{tenant_id}/webhooks/{webhook_id}/histories/{id}/retry/", tags=[_("Webhook")])
def retry_webhook_history(request, tenant_id: str, webhook_id: str, id:str):
    """ 重试webhook历史记录,TODO
    """
    return {}

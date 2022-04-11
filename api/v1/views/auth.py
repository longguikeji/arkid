from enum import Enum
from typing import Any, Dict, Optional, List
from pydantic import Field
from ninja import Schema, Query, ModelSchema
from arkid.core.event import register_and_dispatch_event
from arkid.core.api import api, operation
from arkid.core.models import Tenant
from arkid.core.translation import gettext_default as _



@api.get("/auth/", response=LoginPageOut, auth=None)
def auth(request, data: LoginPageIn):
    tenant_uuid = data.tenant
    tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
    request.tenant = tenant
    
    return {
        'tenant': tenant, 
        'data': {
            'login': None,
            'password': None,
            'register': None,
        }
    }
from django.shortcuts import redirect
from arkid.config import get_app_config
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.error import SuccessDict

@api.get("/tenant/{tenant_id}/docs/redoc/", tags=["文档"])
@operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_docs(request,tenant_id):
    """ 
    """
    return SuccessDict(
        data = {
            "url": get_app_config().get_frontend_host() + "/api/v1/redoc"
        }
    )
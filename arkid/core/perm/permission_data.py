from arkid.core.b64_compress import Compress
from arkid.core.openapi import get_permissions
from arkid.core.models import (
    UserPermissionResult, User, SystemPermission
    Tenant,
)
from arkid.core.api import api
from django.db.models import Q

import collections
import uuid


class PermissionData(object):
    '''
    权限数据的统一处理类
    '''

    def __init__(self):
        pass
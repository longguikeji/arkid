#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue
from enum import Enum
class TypeEnum(str, Enum):
    work = 'work'
    home = 'home'
    mobile = 'mobile'
    fax = 'fax'
    pager = 'pager'
    other = 'other'

class PhoneNumber(TypedValue):
    type: TypeEnum

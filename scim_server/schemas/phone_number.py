#!/usr/bin/env python3
from .typed_value import TypedValue
from enum import Enum
from typing import Optional
class TypeEnum(str, Enum):
    work = 'work'
    home = 'home'
    mobile = 'mobile'
    fax = 'fax'
    pager = 'pager'
    other = 'other'

class PhoneNumber(TypedValue):
    type: Optional[TypeEnum]

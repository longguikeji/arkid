#!/usr/bin/env python3
from enum import Enum
from .typed_value import TypedValue
from typing import Optional

class TypeEnum(str, Enum):
    home = "home"
    other = 'other'
    work = 'work'
class ElectroicMailAddress(TypedValue):
    type: Optional[TypeEnum] 

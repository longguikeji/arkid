#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue
from enum import Enum
from typing import Optional
from pydantic import Field

class TypeEnum(str, Enum):
    direct = 'direct'
    indirect = 'indirect'

class UserGroups(TypedValue):
    type: Optional[TypeEnum]
    ref: Optional[str] = Field(None, alias="$ref")
    display: Optional[str]
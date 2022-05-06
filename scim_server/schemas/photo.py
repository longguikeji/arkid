#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue
from enum import Enum

class TypeEnum(str, Enum):
    photo = 'photo'
    thumbnail = 'thumbnail'

class Photo(TypedValue):
    type: TypeEnum

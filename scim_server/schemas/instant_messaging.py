#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue
from enum import Enum
from typing import Optional
class TypeEnum(str, Enum):
    aim = "aim"
    gtalk = 'gtalk'
    icq = 'icq'
    msn = 'msn'
    qq = 'qq'
    skype = 'skype'
    xmpp = 'xmpp'
    yahoo = 'yahoo'

class InstantMessaging(TypedValue):
    type: TypeEnum

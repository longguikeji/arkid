#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue


class InstantMessagingBase(TypedValue):
    AIM = 'aim'
    Gtalk = 'gtalk'
    Icq = 'icq'
    Msn = 'msn'
    Qq = 'qq'
    Skype = 'skype'
    Xmpp = 'xmpp'
    Yahoo = 'yahoo'

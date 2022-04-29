#!/usr/bin/env python3
from scim_server.schemas.typed_value import TypedValue


class PhoneNumberBase(TypedValue):
    Fax = 'fax'
    Home = 'home'
    Mobile = 'Mobile'
    Other = 'other'
    Pager = 'pager'
    Work = 'work'

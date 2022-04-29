#!/usr/bin/env python3

from .typed_value import TypedValue


class ElectroicMailAddressBase(TypedValue):
    Home = 'home'
    Other = 'other'
    Work = 'work'

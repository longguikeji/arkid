#!/usr/bin/env python3
from enum import Enum

AttributeDataType = Enum(
    'AttributeDataType',
    (
        'string',
        'boolean',
        'decimal',
        'integer',
        'datetime',
        'binary',
        'reference',
        'complex',
    ),
)

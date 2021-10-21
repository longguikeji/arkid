#!/usr/bin/env python3
from enum import Enum

ComparisonOperator = Enum(
    'ComparisonOperator',
    (
        'BitAnd',
        'Endswith',
        'Equals',
        'EqualOrGreaterThan',
        'GreaterThan',
        'Includes',
        'IsMemberOf',
        'MatchesExpression',
        'NotBitAnd',
        'NotEquals',
        'NotMatchesExpression',
    ),
)

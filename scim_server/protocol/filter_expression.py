#!/usr/bin/env python3
import re
from enum import Enum
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.protocol.filter import (
    Filter
)
from scim_server.schemas.attribute_data_type import AttributeDataType
from scim_server.exceptions import (
    ArgumentNullException,
    ArgumentException,
    InvalidOperationException,
    NotSupportedException,
)

ComparisonOperatorValue = Enum(
    'ComparisonOperatorValue',
    (
        'bitAnd',
        'eq',
        'ne',
        'co',
        'sw',
        'ew',
        'ge',
        'gt',
        'includes',
        'isMemberOf',
        'lt',
        'matchesExpression',
        'le',
        'notBitAnd',
        'notMatchesExpression',
    ),
)

LogicalOperatorValue = Enum('LogicalOperatorValue', ('and', 'or'))

COMPARE_OP_MAP = {
    ComparisonOperatorValue.bitAnd: ComparisonOperator.BitAnd,
    ComparisonOperatorValue.ew: ComparisonOperator.Endswith,
    ComparisonOperatorValue.eq: ComparisonOperator.Equals,
    ComparisonOperatorValue.ge: ComparisonOperator.EqualOrGreaterThan,
    ComparisonOperatorValue.gt: ComparisonOperator.GreaterThan,
    ComparisonOperatorValue.includes: ComparisonOperator.Includes,
    ComparisonOperatorValue.isMemberOf: ComparisonOperator.IsMemberOf,
    ComparisonOperatorValue.matchesExpression: ComparisonOperator.MatchesExpression,
    ComparisonOperatorValue.notBitAnd: ComparisonOperator.NotBitAnd,
    ComparisonOperatorValue.ne: ComparisonOperator.NotEquals,
    ComparisonOperatorValue.notMatchesExpression: ComparisonOperator.NotMatchesExpression,
}


class FilterExpression:
    bracket_close = ')'
    escape = '\\'
    quote = '"'

    pattern_group_left = 'left'
    pattern_group_level_up = 'level_up'
    pattern_group_operator = 'operator'
    pattern_group_right = 'right'

    pattern_template = (
        r"(?P<"
        + pattern_group_level_up
        + r">\(*)?(?P<"
        + pattern_group_left
        + r">(\S)*)(\s*(?P<"
        + pattern_group_operator
        + r">{0})\s*(?P<"
        + pattern_group_right
        + r">(.)*))?"
    )

    regular_expression_operator_or = '|'
    space = ' '
    template = '{0} {1} {2}'
    trailing_characters = [quote, space, bracket_close]

    logical_operator_and = 'and'
    logical_operator_or = 'or'

    @classmethod
    def get_comparison_operators(cls):
        result = ''
        for item in ComparisonOperatorValue:
            if result:
                result += FilterExpression.regular_expression_operator_or
            result += item.name
        return result

    @classmethod
    def get_filter_pattern(cls):
        print(cls.pattern_template)
        return cls.pattern_template.format(cls.get_comparison_operators())

    @classmethod
    def get_expression(cls):
        pattern = cls.get_filter_pattern()
        print(pattern)
        return re.compile(pattern)

    def __init__(
        self,
        text='',
        attribute_path='',
        comparison_operator=None,
        filter_operator=None,
        group=0,
        level=0,
        logical_operator=None,
        value=None,
    ):
        self.text = text
        self.attribute_path = attribute_path
        self.comparison_operator = comparison_operator
        self.filter_operator = filter_operator
        self.group = group
        self.level = group
        self.logical_operator = logical_operator
        self.value = value
        self.next = None
        self.previous = None

    @classmethod
    def clone(cls, other):
        if not other:
            raise ArgumentNullException('other')
        instance = cls(
            other.text,
            other.attribute_path,
            other.comparison_operator,
            other.filter_operator,
            other.group,
            other.level,
            other.logical_operator,
            other.value,
        )
        if other.next:
            instance.next = cls.clone(other.next)
            instance.next.previous = instance
        return instance

    @classmethod
    def create(cls, text, group=0, level=0):
        if not text:
            raise ArgumentNullException('text')
        instance = cls()
        instance.text = text.strip()
        instance.level = level
        instance.group = group
        expression = cls.get_expression()
        print(expression)
        matches = expression.finditer(instance.text)
        for match in matches:
            level_up_group = match.group(cls.pattern_group_level_up)
            if level_up_group:
                instance.level += len(level_up_group)
                instance.group += 1

            operator_group = match.group(cls.pattern_group_operator)
            if operator_group:
                left_group = match.group(cls.pattern_group_left)
                right_group = match.group(cls.pattern_group_right)
                instance.initialize(left_group, operator_group, right_group)

            else:
                remaider = match.group(0).strip()
                if not remaider:
                    continue
                elif len(remaider) == 1 and remaider[0] == cls.bracket_close:
                    continue
                else:
                    raise ArgumentException(remaider)
        return instance

    def initialize(self, left, operator, right):
        if not left:
            raise ArgumentNullException(left)
        if not operator:
            raise ArgumentNullException(operator)
        if not right:
            raise ArgumentNullException(right)

        self.attribute_path = left
        if operator not in ComparisonOperatorValue.__members__:
            raise InvalidOperationException(operator)

        self.comparison_operator = ComparisonOperatorValue[operator]
        self.filter_operator = COMPARE_OP_MAP.get(self.comparison_operator)
        if not self.filter_operator:
            raise NotSupportedException(self.comparison_operator.name)

        comparison_value = self.try_parse(right)
        if not comparison_value:
            raise InvalidOperationException(right)
        self.value = ComparisonValue(
            comparison_value, right[0] == FilterExpression.quote
        )
        index_remainder = right.index(comparison_value) + len(comparison_value)
        if index_remainder >= len(right):
            return

        remainder = right[index_remainder:]
        index_and = remainder.find('and')
        index_or = remainder.find('or')
        index_next_filter = 0
        index_logical_operator = 0
        if index_and >= 0 and (index_or < 0 or index_and < index_or):
            index_next_filter = index_and + len('and')
            self.logical_operator = LogicalOperatorValue['and']
            index_logical_operator = index_and
        elif index_or >= 0:
            index_next_filter = index_or + len('or')
            self.logical_operator = LogicalOperatorValue['or']
            index_logical_operator = index_or
        else:
            tail = remainder
            while True:
                if tail and tail[-1] in FilterExpression.trailing_characters:
                    tail = tail.rstrip(tail[-1])
                else:
                    break
            if tail:
                raise InvalidOperationException(self.text)
            else:
                return

        next_expression = remainder[index_next_filter:]
        index_closing_bracket = remainder.find(FilterExpression.bracket_close)
        next_expression_level = 0
        next_expression_group = 0
        if (
            index_closing_bracket >= 0
            and index_closing_bracket < index_logical_operator
        ):
            next_expression_level = self.level - 1
            next_expression_group = self.group + 1
        else:
            next_expression_level = self.level
            next_expression_group = self.group

        self.next = FilterExpression.create(
            next_expression, next_expression_group, next_expression_level
        )
        self.next.previous = self

    @classmethod
    def try_parse(cls, input):
        if not input:
            return ''

        buffer = ''
        if cls.quote == input[0]:
            index = 0
            position = 1
            while True:
                index = input.find(cls.quote, position)
                if index < 0:
                    raise InvalidOperationException()
                if index > 1 and cls.escape == input[index - 1]:
                    position = index + 1
                    continue
                next_character_index = index + 1
                if (
                    next_character_index < len(input)
                    and input[next_character_index] != cls.space
                    and input[next_character_index] != cls.bracket_close
                ):
                    position = next_character_index
                    continue
                break
            buffer = input[1:index]
        else:
            index = input.find(cls.space)
            if index >= 0:
                if input.rfind('and') < index and input.rfind('or') < index:
                    buffer = input
                else:
                    buffer = input[0, index]

            else:
                buffer = input

        comparison_value = buffer
        if input[0] == cls.quote:
            return comparison_value
        else:
            while True:
                if comparison_value[-1] in cls.trailing_characters:
                    comparison_value = comparison_value.rstrip(comparison_value[-1])
                else:
                    break
            return comparison_value

    def to_filter(self):
        result = Filter(self.attribute_path, self.filter_operator, self.value.value)
        result.data_type = self.value.data_type
        return result

    @classmethod
    def and_single_with_single(cls, left, right):
        if not left:
            raise ArgumentNullException(left)
        if not right:
            raise ArgumentNullException(right)
        if not left.additional_filter:
            left.additional_filter = right
        else:
            cls.and_single_with_single(left.additional_filter, right)

    @classmethod
    def and_list_with_single(cls, left, right):
        if not left:
            raise ArgumentNullException(left)
        if not right:
            raise ArgumentNullException(right)
        for filter in left:
            cls.and_single_with_single(filter, right)
        return left

    @classmethod
    def and_single_with_list(cls, left, right):
        result = []
        template = Filter.clone(left)
        for i, item in enumerate(right):
            if i == 0:
                left_filter = left
            else:
                left_filter = Filter.clone(template)
                result.append(left_filter)
            cls.and_single_with_single(left_filter, right)
        return result

    def convert(self):
        result = []
        this_filter = self.to_filter()
        result.append(this_filter)
        current = self.next
        while current:
            if self.level == current.level:
                filter = current.to_filter()
                previous_logical_operator = current.previous.logical_operator
                if previous_logical_operator == LogicalOperatorValue['and']:
                    left = result[-1]
                    FilterExpression.and_single_with_single(left, filter)
                elif previous_logical_operator == LogicalOperatorValue['or']:
                    result.append(filter)
                else:
                    raise NotSupportedException(previous_logical_operator)
                current = current.next
            elif self.level > current.level:
                superiors = current.convert()
                previous_logical_operator = current.previous.logical_operator
                if previous_logical_operator == LogicalOperatorValue['and']:
                    superior = superiors[0]
                    result = FilterExpression.and_list_with_single(result, superior)
                    remainder = superiors[1:]
                    result.extend(remainder)
                elif previous_logical_operator == LogicalOperatorValue['or']:
                    result.extend(superiors)
                else:
                    raise NotSupportedException(previous_logical_operator)
            else:
                subordinate = current
                while (
                    current
                    and self.level < current.level
                    and subordinate.group == current.group
                ):
                    current = current.next
                if current:
                    current.previous.next = None
                    subordinate.previous.next = current
                subordinates = subordinate.convert()
                if subordinate.previous.logical_operator == LogicalOperatorValue['and']:
                    superior = result[-1]
                    merged = FilterExpression.and_single_with_list(
                        superior, subordinates
                    )
                    result.extend(merged)
                elif (
                    subordinate.previous.logical_operator == LogicalOperatorValue['or']
                ):
                    result.extend(subordinates)

                else:
                    raise NotSupportedException(subordinate.previous.logical_operator)
        return result

    def to_filters(self):
        clone = FilterExpression.clone(self)
        result = clone.convert()
        return result


class ComparisonValue:
    template = "\"{0}\""

    def __init__(self, value, quoted):
        if not value:
            raise ArgumentNullException(value)
        self.value = value
        self.quoted = quoted

        if self.quoted:
            self.data_type = AttributeDataType.string
        elif self.value in ('True', 'true', 'False', 'false'):
            self.data_type = AttributeDataType.boolean
        elif self.try_parse_int(value):
            self.data_type = AttributeDataType.integer
        elif self.try_parse_float(value):
            self.data_type = AttributeDataType.decimal
        else:
            self.data_type = AttributeDataType.string

    def try_parse_int(self, value):
        try:
            int(value)
        except ValueError:
            return False
        return True

    def try_parse_float(self, value):
        try:
            float(value)
        except ValueError:
            return False
        return True

    def __str__(self):
        return self.template.format(self.value)

#!/usr/bin/env python3
import uuid
from enum import Enum
from urllib.parse import quote, unquote
from scim_server.protocol.extension import ArgumentNullException
from scim_server.schemas.attribute_data_type import AttributeDataType
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.exceptions import NotSupportedException


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


class Filter:
    comparison_value_template = '\"{0}\"'
    template = 'filter={0}'
    template_comparison = '{0} {1} {2}'
    template_conjunction = '{0} {1} {2}'
    template_nesting = "({0})"

    @property
    def comparison_value(self):
        return self._comparison_value

    @comparison_value.setter
    def comparison_value(self, value):
        self._comparison_value = value
        self._comparison_value_encoded = quote(value)

    @property
    def comparison_value_encoded(self):
        return self._comparison_value_encoded

    @property
    def additional_filter(self):
        return self._additional_filter

    @additional_filter.setter
    def additional_filter(self, value):
        self._additional_filter = value

    @property
    def attribute_path(self):
        return self._attribute_path

    @attribute_path.setter
    def attribute_path(self, value):
        self._attribute_path = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = value

    @property
    def filter_operator(self):
        return self._filter_operator

    @filter_operator.setter
    def filter_operator(self, value):
        self._filter_operator = value

    def __init__(self, attribute_path, filter_operator, comparison_value):
        if not attribute_path:
            raise ArgumentNullException('attribute_path')
        if not comparison_value:
            raise ArgumentNullException('filter_operator')

        self.attribute_path = attribute_path
        self.filter_operator = filter_operator
        self.comparison_value = comparison_value
        self.data_type = AttributeDataType.string

    @classmethod
    def clone(cls, other):
        if not other:
            raise ArgumentNullException('other')
        res = cls(other.attribute_path, other.filter_operator, other.comparison_value)
        res.data_type = other.data_type
        if other.additional_filter is not None:
            res.additional_filter = Filter.filter(other.AdditionalFilter)

    def __str__(self):
        result = self.serialize()
        return result

    def serialize(self):
        operator_value = None
        compare_op_map = {
            ComparisonOperator.BitAnd: ComparisonOperatorValue.bitAnd,
            ComparisonOperator.EndsWith: ComparisonOperatorValue.ew,
            ComparisonOperator.Equals: ComparisonOperatorValue.eq,
            ComparisonOperator.EqualOrGreaterThan: ComparisonOperatorValue.ge,
            ComparisonOperator.GreaterThan: ComparisonOperatorValue.gt,
            ComparisonOperator.Includes: ComparisonOperatorValue.includes,
            ComparisonOperator.IsMemberOf: ComparisonOperatorValue.isMemberOf,
            ComparisonOperator.MatchesExpression: ComparisonOperatorValue.matchesExpression,
            ComparisonOperator.NotBitAnd: ComparisonOperatorValue.notBitAnd,
            ComparisonOperator.NotEquals: ComparisonOperatorValue.ne,
            ComparisonOperator.NotMatchesExpression: ComparisonOperatorValue.notMatchesExpression,
        }
        operator_value = compare_op_map.get(self.filter_operator, None)
        if not operator_value:
            raise NotSupportedException(self.filter_operator)

        effective_data_type = self.data_type or AttributeDataType.string
        if effective_data_type in (
            AttributeDataType.boolean,
            AttributeDataType.decimal,
            AttributeDataType.integer,
        ):
            right_hand_side = self.comparison_value

        else:
            right_hand_side = self.comparison_value_template.format(
                self.comparison_value
            )
        filter_str = self.template_comparison.format(
            self.attribute_path, operator_value.name, right_hand_side
        )
        result = ''
        if self.additional_filter:
            additional_filter_str = self.additional_filter.serialize()
            result = self.template_conjunction.format(
                filter_str, LogicalOperatorValue['and'].name, additional_filter_str
            )
        else:
            result = filter

        return result

    @staticmethod
    def to_string(filters):
        if not filters:
            raise ArgumentNullException('filters')

        placeholder = uuid.uuid4().hex
        all_filters = ''
        for filter in filters:
            clone = Filter.clone(filter)
            clone.comparison_value = placeholder
            current_filter = clone.serialize()
            encoded_filter = quote(current_filter).replace(
                placeholder, filter.comparison_value_encoded
            )
            if not all_filters:
                all_filters = (
                    Filter.template_nesting.format(encoded_filter)
                    if len(filters) > 1
                    else encoded_filter
                )
            else:
                right_hand_side = (
                    Filter.template_nesting.format(encoded_filter)
                    if (filter.additional_filter or len(filters) > 1)
                    else encoded_filter
                )

                all_filters = Filter.template_conjunction.format(
                    all_filters, LogicalOperatorValue['or'].name, right_hand_side
                )

        result = Filter.template.format(all_filters)
        return result

    @staticmethod
    def try_parse(filter_expression):
        from scim_server.protocol.filter_expression import FilterExpression
        expression = unquote(filter_expression).strip()
        if not expression:
            raise ArgumentNullException('filter expression')
        try:
            expression = FilterExpression.create(filter_expression)
            filters = expression.to_filters()
            return filters
        except Exception as e:
            return None

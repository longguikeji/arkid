#!/usr/bin/env python3
import re
from scim_server.exceptions import ArgumentNullException, ArgumentException
from scim_server.schemas.schema_constants import SchemaConstants
from scim_server.protocol.filter import Filter


class Path:
    ArgumentNamePathExpression = "pathExpression"

    ConstructNameSubAttributes = "subAttr"
    ConstructNameValuePath = "valuePath"
    PatternTemplate = r"(?P<{0}>.*)\[(?P<{1}>.*)\]"
    SchemaIdentifierSubnamespace = "urn:ietf:params:scim:schemas:"
    Pattern = PatternTemplate.format(ConstructNameValuePath, ConstructNameSubAttributes)
    RegularExpression = re.compile(Pattern)
    SeperatorAttributes = '.'

    def __init__(self, path_expression):
        if not path_expression:
            raise ArgumentNullException(Path.ArgumentNamePathExpression)
        self.expression = path_expression

        self.attribute_path = ''
        self.schema_identifier = ''
        self.sub_attributes = []
        self.value_path = None

    @classmethod
    def create(cls, path_expression):
        if not path_expression:
            raise ArgumentNullException(Path.ArgumentNamePathExpression)
        result = Path.try_parse(path_expression)
        if not result:
            raise ArgumentException(path_expression)
        return result

    @classmethod
    def try_extract_schema_identifier(cls, path_expression):
        schema_identifier = ''
        if not path_expression:
            return ''
        if not path_expression.startswith(Path.SchemaIdentifierSubnamespace):
            return ''
        seperator_index = path_expression.rfind(SchemaConstants.SeparatorSchemaIdentifierAttribute)
        if seperator_index == -1:
            return ''
        schema_identifier = path_expression[0:seperator_index]
        return schema_identifier

    @classmethod
    def try_parse(cls, path_expression):
        if not path_expression:
            raise ArgumentNullException(Path.ArgumentNamePathExpression)
        buffer = cls(path_expression)
        expression = path_expression
        schema_identifier = Path.try_extract_schema_identifier(path_expression)
        if schema_identifier:
            expression = expression[len(schema_identifier) + 1 :]
            buffer.schema_identifier = schema_identifier

        seperator_index = expression.find(Path.SeperatorAttributes)
        if seperator_index >= 0:
            value_path_expression = expression[seperator_index + 1 :]
            expression = expression[0:seperator_index]
            value_path = Path.try_parse(value_path_expression)
            if not value_path:
                return None
            buffer.value_path = value_path
            buffer.sub_attributes = []
        match = cls.RegularExpression.match(expression)
        if not match:
            buffer.attribute_path = expression
            buffer.sub_attributes = []
        else:
            buffer.attribute_path = match.group(cls.ConstructNameValuePath)
            filter_expression = match.group(cls.ConstructNameSubAttributes)
            filters = Filter.try_parse(filter_expression)
            if not filters:
                return None
            buffer.sub_attributes = filters
        return buffer

    def __str__(self):
        return self.expression

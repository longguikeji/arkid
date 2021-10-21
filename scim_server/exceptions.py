#!/usr/bin/env python3
from scim_server.protocol.protocol_schema_identifiers import ProtocolSchemaIdentifiers


class SCIMException(Exception):
    status = 500
    schema = ProtocolSchemaIdentifiers.Version2Error
    scim_type = None

    def __init__(self, detail=None, **kwargs):
        self.detail = detail or ''
        self.status = kwargs.get('status') or self.status
        self.schemas = kwargs.get('schemas') or [self.schema]
        self.scim_type = kwargs.get('scim_type') or self.scim_type

        msg = '({} {}) {}'.format(self.status, self.scim_type, self.detail)

        super(Exception, self).__init__(msg)

    def to_dict(self):
        d = {
            'schemas': self.schemas,
            'detail': self.detail,
            'status': self.status,
        }
        if self.scim_type:
            d['scimType'] = self.scim_type

        return d


class AuthorizationException(SCIMException):
    status = 401


class NotFoundException(SCIMException):
    status = 404

    def __init__(self, uuid, **kwargs):
        detail = u'Resource {} not found'.format(uuid)
        super(NotFoundException, self).__init__(detail, **kwargs)


class BadRequestException(SCIMException):
    status = 400


class IntegrityException(SCIMException):
    status = 409


class NotImplementedException(SCIMException):
    status = 501


class ArgumentException(SCIMException):
    status = 400


class ArgumentNullException(ArgumentException):
    status = 400


class InvalidOperationException(SCIMException):
    status = 400


class NotSupportedException(SCIMException):
    status = 501


class NotAcceptableException(SCIMException):
    status = 406


class ConflictException(SCIMException):
    status = 409

#!/usr/bin/env python
import uuid
from scim_server.service.provider_base import ProviderBase
from scim_server.mssql_provider.mssql_storage import get_mssql_config
from scim_server.exceptions import (
    ArgumentException,
    ArgumentNullException,
    BadRequestException,
    ConflictException,
    NotSupportedException,
    NotFoundException,
)
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.phone_number import PhoneNumber
from scim_server.schemas.manager import Manager
from scim_server.schemas.name import Name

UserSql = 'select A.femp_id, A.fcode, A.fname, A.fcard_no, A.fstatus, A.fjob, B.fid as dept_id, B.ffull_name as dept_name, C.fjob_name, D.COMPNAME, E.fname as manager_name, E.femp_id as manager_id from emp A left join dept B on A.fdept_id = B.fid left join job C on A.fjob = C.fjob_code left join ECOMPANY D on B.fcomp = D.COMPID left join Emp E on A.freport_man = E.Fcode'
UserExtensionSchema = 'urn:ietf:params:scim:schemas:extension:hr:2.0:User'


class MssqlUserProvider(ProviderBase):
    def __init__(self):
        self.db_config = get_mssql_config()
        if not self.db_config:
            raise BadRequestException('No sql server config found')

    def create_async2(self, resource, correlation_identifier):
        if resource.identifier is not None:
            raise BadRequestException()

        if not resource.user_name:
            raise BadRequestException()

        existing_users = self.storage.users.values()
        for item in existing_users:
            if item.user_name == resource.user_name:
                raise ConflictException()
        resource_identifier = uuid.uuid4().hex
        resource.identifier = resource_identifier
        self.storage.users[resource_identifier] = resource

        return resource

    def delete_async2(self, resource_identifier, correlation_identifier):
        if not resource_identifier.identifier:
            raise BadRequestException()
        identifier = resource_identifier.identifier

        if identifier in self.storage.users:
            del self.storage.users[identifier]

    def query_async2(self, parameters, correlation_identifier):
        if parameters is None:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            all_users = []
            conn = self.db_config.get_connection()
            cursor = conn.cursor(as_dict=True)
            cursor.execute(UserSql)
            row = cursor.fetchone()
            while row:
                user = self.convert_record_to_user(row)
                all_users.append(user)
                row = cursor.fetchone()
            conn.close()
            return all_users

        query_filter = parameters.alternate_filters[0]
        if not query_filter.attribute_path:
            raise ArgumentException('invalid parameters')
        if not query_filter.comparison_value:
            raise ArgumentException('invalid parameters')
        if query_filter.filter_operator != ComparisonOperator.Equals:
            raise NotSupportedException('unsupported comparison operator')

        if query_filter.attribute_path == AttributeNames.UserName:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(as_dict=True)
            sql = UserSql + ' where A.fcode={}'.format(query_filter.comparison_value)
            cursor.execute(sql)
            row = cursor.fetchone()
            conn.close()
            if row:
                user = self.convert_record_to_user(row)
                return [user]
            else:
                return []

        raise NotSupportedException('unsupported filter')

    def replace_async2(self, resource, correlation_identifier):
        if not resource.identifier:
            raise BadRequestException()
        if not resource.user_name:
            raise BadRequestException()

        existing_users = self.storage.users.values()
        for item in existing_users:
            if item.user_name == resource.user_name:
                raise ConflictException()
        if resource.identifier not in self.storage.users:
            raise NotFoundException()

        self.storage.users[resource.identifier] = resource
        return resource

    def retrieve_async2(self, parameters, correlation_identifier):
        if not parameters:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if not parameters.resource_identifier.identifier:
            raise ArgumentNullException('parameters')

        identifier = parameters.resource_identifier.identifier
        conn = self.db_config.get_connection()
        cursor = conn.cursor(as_dict=True)
        sql = UserSql + ' where A.femp_id={}'.format(identifier)
        cursor.execute(sql)
        row = cursor.fetchone()
        conn.close()
        if row:
            user = self.convert_record_to_user(row)
            return user
        else:
            raise NotFoundException(identifier)

    def update_async2(self, patch, correlation_identifier):
        if not patch:
            raise ArgumentNullException('patch')
        if not patch.resource_identifier:
            raise ArgumentException('Invalid patch')
        if not patch.resource_identifier.identifier:
            raise ArgumentException('invalid patch')
        if not patch.patch_request:
            raise ArgumentException('invalid patch')
        user = self.storage.users.get(patch.resource_identifier.identifier)
        if user:
            user.apply(patch.patch_request)
        else:
            raise NotFoundException(patch.resource_identifier.identifier)

    def convert_record_to_user(self, record):
        user = Core2EnterpriseUser()
        user.identifier = record.get('femp_id')
        user.user_name = record.get('fcode')
        user.enterprise_extension.department = record.get('dept_name', '').strip()
        user.title = record.get('fjob_name')
        user.enterprise_extension.manager = Manager.from_dict(
            {
                'value': record.get('manager_id'),
                'displayName': record.get('manager_name'),
            }
        )
        phone_number = record.get('fcard_no')
        user_full_name = record.get('fname')
        user.name = Name.from_dict(
            {
                'formatted': user_full_name,
                'familyName': user_full_name[0],
                'givenName': user_full_name[1:],
            }
        )
        if phone_number:
            user.phone_numbers = [
                PhoneNumber.from_dict({'type': 'work', 'value': phone_number})
            ]

        user.add_custom_attribute(
            UserExtensionSchema,
            {'FCOMP': record.get('COMPNAME'), 'FSTATUS': record.get('fstatus'), 'FDEPT_ID': record.get('dept_id')},
        )
        user.add_schema(UserExtensionSchema)
        return user

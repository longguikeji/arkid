#!/usr/bin/env python
import uuid
from scim_server.service.provider_base import ProviderBase
from scim_server.mssql_provider.mssql_storage import get_mssql_config
from scim_server.exceptions import (
    ArgumentException,
    ArgumentNullException,
    BadRequestException,
    NotSupportedException,
    NotFoundException,
    NotImplementedException,
    ConflictException,
)
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.core2_enterprise_user import Core2EnterpriseUser
from scim_server.schemas.phone_number import PhoneNumber
from scim_server.schemas.manager import Manager
from scim_server.schemas.name import Name
from scim_server.protocol.path import Path
from scim_server.schemas.schema_identifiers import SchemaIdentifiers
from .utils import get_connection, get_scim_user
from .constants import UserExtensionSchema


class MssqlUserProvider(ProviderBase):
    def __init__(self, config, user_attr_map=None):
        self.user_attr_map = {
            'FEMP_ID': 'id',
            'FCODE': 'userName',
            'DEPT_NAME': 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:department',
            'FJOB_NAME': 'title',
            'MANAGER_ID': 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:manager.value',
            'MANAGER_NAME': 'urn:ietf:params:scim:schemas:extension:enterprise:2.0:User:manager.displayName',
            'FCARD_NO': 'phoneNumbers[type eq "mobile"].value',
            'FNAME': 'name.formatted',
            'FAMILY_NAME': 'name.familyName',
            'GIVEN_NAME': 'name.givenName',
            'email': 'emails[type eq "work"].value',
            'FCOMP': 'urn:ietf:params:scim:schemas:extension:hr:2.0:User:FCOMP',
            'FSTATUS': 'urn:ietf:params:scim:schemas:extension:hr:2.0:User:FSTATUS',
            'FCOMP_ID': 'urn:ietf:params:scim:schemas:extension:hr:2.0:User:FCOMP_ID',
            'FDEPT_ID': 'urn:ietf:params:scim:schemas:extension:hr:2.0:User:FDEPT_ID',
        }
        self.config = config
        self.db_config = config.data
        if not self.db_config:
            raise BadRequestException('No sql server config found')

    def create_async2(self, resource, correlation_identifier):
        raise NotImplementedException('Not implemented')

    def delete_async2(self, resource_identifier, correlation_identifier):
        raise NotImplementedException('Not implemented')

    def get_db_users(self, where_clause=None, args=None):

        emp_table = self.db_config.get('emp_table')
        dept_table = self.db_config.get('dept_table')
        job_table = self.db_config.get('job_table')
        company_table = self.db_config.get('company_table')
        UserSql = f'''
        SELECT  A.FEMP_ID, A.FCODE, A.FNAME, A.FCARD_NO, A.FSTATUS, A.FJOB, A.email, B.FID AS DEPT_ID, B.FFULL_NAME AS DEPT_NAME, B.FCOMP AS FCOMP_ID,
                C.FJOB_NAME, D.COMPNAME, E.FNAME AS MANAGER_NAME, E.FEMP_ID AS MANAGER_ID
        FROM    {emp_table} AS A LEFT OUTER JOIN
                {dept_table} AS B ON A.FDEPT_ID = B.FID LEFT OUTER JOIN
                {job_table} AS C ON A.FJOB = C.fjob_code LEFT OUTER JOIN
                {company_table} AS D ON B.FCOMP = D.COMPID LEFT OUTER JOIN
                {emp_table} AS E ON A.FREPORT_MAN = E.FCODE
        '''

        all_users = []
        conn = get_connection(self.db_config)
        cursor = conn.cursor(as_dict=True)
        cursor.execute(UserSql)
        row = cursor.fetchone()
        while row:
            row = self.format_record(row)
            user = get_scim_user(row, self.user_attr_map)
            # user = self.convert_record_to_user(row)
            all_users.append(user)
            row = cursor.fetchone()
        conn.close()
        return all_users

    def format_record(self, row):
        row['FCOMP'] = row.get('COMPNAME')
        row['FDEPT_ID'] = row.get('DEPT_ID')
        full_name = row.get('FNAME')
        if full_name:
            row['FAMILY_NAME'] = full_name[0]
            row['GIVEN_NAME'] = full_name[1:]
        row['MANAGER_ID'] = str(row.get('MANAGER_ID', ''))
        row['FCODE'] = str(row.get('FCODE', ''))
        phone_number = row.get('FCARD_NO')
        try:
            phone_number = int(phone_number)
        except TypeError:
            pass
        else:
            phone_number = format(phone_number, 'X')
            row['FCARD_NO'] = phone_number
        return row

    def query_async2(self, parameters, correlation_identifier):
        if parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            # return self.get_db_users()
            return self.get_db_users()

        query_filter = parameters.alternate_filters[0]
        if not query_filter.attribute_path:
            raise ArgumentException('invalid parameters')
        if not query_filter.comparison_value:
            raise ArgumentException('invalid parameters')
        if query_filter.filter_operator != ComparisonOperator.Equals:
            raise NotSupportedException('unsupported comparison operator')

        if query_filter.attribute_path == AttributeNames.UserName:
            where_clause = "WHERE FCODE = %s"
            return self.get_db_users(
                where_clause=where_clause, args=query_filter.comparison_value
            )

        raise NotSupportedException('unsupported filter')

    def replace_async2(self, resource, correlation_identifier):
        raise NotImplementedException('Not implemented')

    def retrieve_async2(self, parameters, correlation_identifier):
        if not parameters:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if not parameters.resource_identifier.identifier:
            raise ArgumentNullException('parameters')

        identifier = parameters.resource_identifier.identifier
        where_clause = "WHERE FEMP_ID = %s"
        rows = self.get_db_users(where_clause=where_clause, args=identifier)
        if rows and len(rows) == 1:
            user = rows[0]
            return user
        elif len(rows) > 1:
            raise ConflictException('Duplicated identifier found')
        else:
            raise NotFoundException(identifier)

    def update_async2(self, patch, correlation_identifier):
        raise NotImplementedException

    # def convert_record_to_user(self, record):
    #     user = Core2EnterpriseUser()
    #     user.identifier = record.get('FEMP_ID')
    #     user.user_name = str(record.get('FCODE', ''))
    #     user.enterprise_extension.department = record.get('DEPT_NAME')
    #     user.title = record.get('FJOB_NAME')
    #     user.enterprise_extension.manager = Manager.from_dict(
    #         {
    #             'value': str(record.get('MANAGER_ID', '')),
    #             'displayName': record.get('MANAGER_NAME'),
    #         }
    #     )
    #     phone_number = record.get('FCARD_NO')
    #     user_full_name = record.get('FNAME')
    #     user.name = Name.from_dict(
    #         {
    #             'formatted': user_full_name,
    #             'familyName': user_full_name[0],
    #             'givenName': user_full_name[1:],
    #         }
    #     )
    #     if phone_number:
    #         try:
    #             phone_number = int(phone_number)
    #         except TypeError:
    #             pass
    #         else:
    #             phone_number = format(phone_number, 'X')
    #         user.phone_numbers = [
    #             PhoneNumber.from_dict({'type': 'work', 'value': phone_number})
    #         ]

    #     user.add_custom_attribute(
    #         UserExtensionSchema,
    #         {
    #             'FCOMP': record.get('COMPNAME'),
    #             'FSTATUS': record.get('FSTATUS'),
    #             'FCOMP_ID': record.get('FCOMP_ID'),
    #             'FDEPT_ID': record.get('DEPT_ID'),
    #         },
    #     )
    #     user.add_schema(UserExtensionSchema)
    #     return user

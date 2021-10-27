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

UserSql = '''
SELECT  A.FEMP_ID, A.FCODE, A.FNAME, A.FCARD_NO, A.FSTATUS, A.FJOB, B.FID AS DEPT_ID, B.FFULL_NAME AS DEPT_NAME, B.FCOMP AS FCOMP_ID,
        C.FJOB_NAME, D.COMPNAME, E.FNAME AS MANAGER_NAME, E.FEMP_ID AS MANAGER_ID
FROM    EMP AS A LEFT OUTER JOIN
        DEPT AS B ON A.FDEPT_ID = B.FID LEFT OUTER JOIN
        JOB AS C ON A.FJOB = C.fjob_code LEFT OUTER JOIN
        ECOMPANY AS D ON B.FCOMP = D.COMPID LEFT OUTER JOIN
        EMP AS E ON A.FREPORT_MAN = E.FCODE
'''
UserExtensionSchema = 'urn:ietf:params:scim:schemas:extension:hr:2.0:User'


class MssqlUserProvider(ProviderBase):
    def __init__(self):
        self.db_config = get_mssql_config()
        if not self.db_config:
            raise BadRequestException('No sql server config found')

    def create_async2(self, resource, correlation_identifier):
        raise NotImplementedException('Not implemented')

    def delete_async2(self, resource_identifier, correlation_identifier):
        raise NotImplementedException('Not implemented')

    def get_db_users(self, where_clause=None, args=None):
        all_users = []
        conn = self.db_config.get_connection()
        cursor = conn.cursor(as_dict=True)
        conn2 = self.db_config.get_connection()
        cursor2 = conn2.cursor(as_dict=True)

        emp_table = self.db_config.emp_table
        dept_table = self.db_config.dept_table
        job_table = self.db_config.job_table
        company_table = self.db_config.company_table

        user_sql = f'SELECT FEMP_ID, FCODE, FNAME, FCARD_NO, FSTATUS, FJOB, FREPORT_MAN, FDEPT_ID FROM {emp_table}'
        if where_clause:
            user_sql = user_sql + ' ' + where_clause
        cursor.execute(user_sql, args)
        user_row = cursor.fetchone()
        while user_row:
            print('-----------------------')
            print(user_row)
            dept_rows = None
            job_rows = None
            comp_rows = None
            manager_rows = None

            # dept info
            if user_row.get('FDEPT_ID'):
                dept_sql = f'SELECT FCOMP, FFULL_NAME FROM {dept_table} WHERE FID = %d'
                cursor2.execute(dept_sql, user_row.get('FDEPT_ID'))
                dept_rows = cursor2.fetchall()
            # job info
            if user_row.get('FJOB'):
                job_sql = f'SELECT FJOB_NAME FROM {job_table} WHERE FJOB_CODE = %s'
                cursor2.execute(job_sql, user_row.get('FJOB'))
                job_rows = cursor2.fetchall()

            # company info
            if dept_rows:
                comp_sql = f'SELECT COMPNAME FROM {company_table} WHERE COMPID = %d'
                cursor2.execute(comp_sql, dept_rows[0].get('FCOMP'))
                comp_rows = cursor2.fetchall()

            # manager info
            if user_row.get('FREPORT_MAN'):
                manager_sql = (
                    f'SELECT FNAME, FEMP_ID FROM {emp_table} WHERE FEMP_ID = %d'
                )
                cursor2.execute(manager_sql, user_row.get('FREPORT_MAN'))

            user = self.convert_record_to_user(
                user_row, dept_rows, job_rows, comp_rows, manager_rows
            )
            all_users.append(user)
            user_row = cursor.fetchone()
        conn.close()
        conn2.close()
        return all_users

    def get_db_users2(self, where_clause=None, args=None):
        all_users = []
        conn = self.db_config.get_connection()
        cursor = conn.cursor(as_dict=True)
        cursor.execute(UserSql)
        row = cursor.fetchone()
        while row:
            print('++++++++++++++++++++++++++++')
            print(row)
            user = self.convert_record_to_user2(row)
            all_users.append(user)
            row = cursor.fetchone()
        conn.close()
        return all_users

    def query_async2(self, parameters, correlation_identifier):
        if parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            # return self.get_db_users()
            return self.get_db_users2()

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

    def convert_record_to_user(
        self, user_row, dept_rows, job_rows, comp_rows, manager_rows
    ):
        user = Core2EnterpriseUser()
        user.identifier = int(user_row.get('FEMP_ID'))
        user.user_name = user_row.get('FCODE')

        if dept_rows:
            user.enterprise_extension.department = (
                dept_rows[0].get('FFULL_NAME', '').strip()
            )

        if job_rows:
            user.title = job_rows[0].get('FJOB_NAME')

        manager_dict = {'value': user_row.get('FREPORT_MAN')}
        if manager_rows:
            manager_dict.update(displayName=manager_rows[0].get('FNAME'))

        user.enterprise_extension.manager = Manager.from_dict(manager_dict)

        user_full_name = user_row.get('FNAME')
        user.name = Name.from_dict(
            {
                'formatted': user_full_name,
                'familyName': user_full_name[0],
                'givenName': user_full_name[1:],
            }
        )
        phone_number = user_row.get('FCARD_NO')
        if phone_number:
            try:
                phone_number = int(phone_number)
            except TypeError:
                pass
            else:
                phone_number = format(phone_number, 'X')
            user.phone_numbers = [
                PhoneNumber.from_dict({'type': 'work', 'value': phone_number})
            ]
        extension_dict = {
            'FSTATUS': user_row.get('FSTATUS'),
            'FDEPT_ID': user_row.get('FDEPT_ID'),
        }
        if dept_rows:
            fcomp_id = dept_rows[0].get('FCOMP')
            extension_dict.update(FCOMP_ID=fcomp_id)
        if comp_rows:
            fcomp = comp_rows[0].get('COMPNAME')
            extension_dict.update(FCOMP=fcomp)
        user.add_custom_attribute(UserExtensionSchema, extension_dict)
        user.add_schema(UserExtensionSchema)
        return user

    def convert_record_to_user2(self, record):
        user = Core2EnterpriseUser()
        user.identifier = record.get('FEMP_ID')
        user.user_name = record.get('FCODE')
        user.enterprise_extension.department = record.get('DEPT_NAME')
        user.title = record.get('FJOB_NAME')
        user.enterprise_extension.manager = Manager.from_dict(
            {
                'value': record.get('MANAGER_ID'),
                'displayName': record.get('MANAGER_NAME'),
            }
        )
        phone_number = record.get('FCARD_NO')
        user_full_name = record.get('FNAME')
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
            {
                'FCOMP': record.get('COMPNAME'),
                'FSTATUS': record.get('FSTATUS'),
                'FCOMP_ID': record.get('FCOMP_ID'),
                'FDEPT_ID': record.get('DEPT_ID'),
            },
        )
        user.add_schema(UserExtensionSchema)
        return user

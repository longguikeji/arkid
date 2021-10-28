#!/usr/bin/env python3

import uuid
from scim_server.service.provider_base import ProviderBase
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
from scim_server.schemas.core2_group import Core2Group
from scim_server.mssql_provider.mssql_storage import get_mssql_config
from scim_server.schemas.member import Member

GroupExtensionSchema = 'urn:ietf:params:scim:schemas:extension:hr:2.0:Group'


class MssqlGroupProvider(ProviderBase):
    def __init__(self):
        self.db_config = get_mssql_config()
        if not self.db_config:
            raise BadRequestException('No sql server config found')

    def create_async2(self, resource, correlation_identifier):
        if not resource.identifier:
            raise BadRequestException()

        if not resource.display_name:
            raise BadRequestException()

        existing_groups = self.storage.groups.values()
        for item in existing_groups:
            if item.display_name == resource.display_name:
                raise ConflictException()
        resource_identifier = uuid.uuid4().hex
        resource.identifier = resource_identifier
        self.storage.groups[resource_identifier] = resource

        return resource

    def delete_async2(self, resource_identifier, correlation_identifier):
        if not resource_identifier.identifier:
            raise BadRequestException()
        identifier = resource_identifier.identifier

        if identifier in self.storage.groups:
            del self.storage.groups[identifier]

    def query_async2(self, parameters, correlation_identifier):
        if not parameters:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if parameters.alternate_filters is None:
            raise ArgumentException('Invalid parameters')

        if not parameters.schema_identifier:
            raise ArgumentException('Invalid parameters')

        if not parameters.alternate_filters:
            all_groups = []
            conn = self.db_config.get_connection()
            cursor = conn.cursor(as_dict=True)
            conn_member = self.db_config.get_connection()
            cursor_member = conn_member.cursor(as_dict=True)

            dept_table = self.db_config.dept_table
            company_table = self.db_config.company_table
            GroupSql = f'select A.fid, A.ffull_name, A.fcomp, A.fstatus, A.fmanager, B.compname from {dept_table} as A left join {company_table} B on A.fcomp = B.compid'
            cursor.execute(GroupSql)
            row = cursor.fetchone()
            while row:
                print('-----------------------------')
                print(row)
                member_sql = (
                    f'select fid, ffull_name from {dept_table} where fparent_id = %d'
                )
                cursor_member.execute(member_sql, row.get('fid'))
                all_members = cursor_member.fetchall()
                group = self.convert_record_to_group(row, all_members)
                all_groups.append(group)
                row = cursor.fetchone()
            conn.close()
            conn_member.close()
            return all_groups

        query_filter = parameters.alternate_filters[0]
        if not query_filter.attribute_path:
            raise ArgumentException('invalid parameters')
        if not query_filter.comparison_value:
            raise ArgumentException('invalid parameters')
        if query_filter.filter_operator != ComparisonOperator.Equals:
            raise NotSupportedException('unsupported comparison operator')

        if query_filter.attribute_path == AttributeNames.DisplayName:
            conn = self.db_config.get_connection()
            cursor = conn.cursor(as_dict=True)
            sql = GroupSql + ' where A.ffull_name = %s'
            cursor.execute(sql, query_filter.comparison_value)
            rows = cursor.fetchall()
            if len(rows) == 1:
                member_sql = (
                    f'select fid, ffull_name from {dept_table} where fparent_id = %d'
                )
                cursor.execute(member_sql, rows[0].get('fid'))
                all_members = cursor.fetchall()
                conn.close()
                group = self.convert_record_to_group(rows[0], all_members)
                return [group]
            elif len(rows) > 1:
                raise ConflictException('Duplicated displayName found')
            else:
                return []

        raise NotSupportedException('unsupported comparison operator')

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

        dept_table = self.db_config.dept_table
        company_table = self.db_config.company_table
        identifier = parameters.resource_identifier.identifier
        conn = self.db_config.get_connection()
        cursor = conn.cursor(as_dict=True)
        GroupSql = f'select A.fid, A.ffull_name, A.fcomp, A.fstatus, B.compname from {dept_table} as A left join {company_table} B on A.fcomp = B.compid'
        sql = GroupSql + ' where A.fid = %d'
        cursor.execute(sql, identifier)
        rows = cursor.fetchall()
        if len(rows) == 1:
            member_sql = 'select fid, ffull_name from dept where fparent_id = %d'
            cursor.execute(member_sql, rows[0].get('fid'))
            all_members = cursor.fetchall()
            conn.close()
            group = self.convert_record_to_group(rows[0], all_members)
            return group
        elif len(rows) > 1:
            raise ConflictException('Duplicated identifier found')
        raise NotFoundException()

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
            raise NotFoundException()

    def convert_record_to_group(self, record, members):
        group = Core2Group()
        if members:
            group.members = []
        group.identifier = str(record.get('fid', ''))
        group.display_name = record.get('ffull_name', '').strip()
        for item in members:
            member = Member()
            member.display = item.get('ffull_name', '').strip()
            member.value = str(item.get('fid', ''))
            group.members.append(member)

        group_manager = record.get('fmanager')
        if group_manager:
            if ':' in group_manager:
                manager_fcode = group_manager.split(':')[0]
            elif '：' in group_manager:
                manager_fcode = group_manager.split('：')[0]
            else:
                manager_fcode = ''

        group.add_custom_attribute(
            GroupExtensionSchema,
            {
                'FCOMP': record.get('compname'),
                'FSTATUS': record.get('fstatus'),
                'FCOMP_ID': record.get('fcomp'),
                'FMANAGER': manager_fcode,
            },
        )
        group.add_schema(GroupExtensionSchema)
        return group

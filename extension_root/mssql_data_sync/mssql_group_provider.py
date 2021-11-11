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
    NotImplementedException,
)
from scim_server.schemas.comparison_operator import ComparisonOperator
from scim_server.schemas.attribute_names import AttributeNames
from scim_server.schemas.core2_group import Core2Group
from scim_server.mssql_provider.mssql_storage import get_mssql_config
from scim_server.schemas.member import Member
from .utils import get_connection, get_scim_group

GroupExtensionSchema = 'urn:ietf:params:scim:schemas:extension:hr:2.0:Group'


class MssqlGroupProvider(ProviderBase):
    def __init__(self, config, group_attr_map=None):
        self.group_attr_map = {
            'FID': 'id',
            'FFULL_NAME': 'displayName',
            'FCOMP': 'urn:ietf:params:scim:schemas:extension:hr:2.0:Group:FCOMP',
            'FSTATUS': 'urn:ietf:params:scim:schemas:extension:hr:2.0:Group:FSTATUS',
            'FCOMP_ID': 'urn:ietf:params:scim:schemas:extension:hr:2.0:Group:FCOMP_ID',
            'FMANAGER': 'urn:ietf:params:scim:schemas:extension:hr:2.0:Group:FMANAGER',
        }
        self.config = config
        self.db_config = config.data
        if not self.db_config:
            raise BadRequestException('No sql server config found')

    def get_scim_group(self, row, members, group_attr_map):
        group = Core2Group()

    def get_db_groups(self, where_clause=None, args=None):
        all_groups = []
        conn = get_connection(self.db_config)
        cursor = conn.cursor(as_dict=True)
        conn_member = get_connection(self.db_config)
        cursor_member = conn_member.cursor(as_dict=True)

        dept_table = self.db_config.get('dept_table')
        company_table = self.db_config.get('company_table')
        GroupSql = f'SELECT A.FID, A.FFULL_NAME, A.FCOMP, A.FSTATUS, A.FMANAGER, B.COMPNAME FROM {dept_table} AS A LEFT JOIN {company_table} B ON A.FCOMP = B.COMPID'
        cursor.execute(GroupSql)
        row = cursor.fetchone()
        while row:
            self.format_record(row)
            member_sql = (
                f'SELECT FID, FFULL_NAME FROM {dept_table} WHERE FPARENT_ID = %d'
            )
            cursor_member.execute(member_sql, row.get('FID'))
            all_members = cursor_member.fetchall()
            for item in all_members:
                self.format_record(item)
            # group = self.convert_record_to_group(row, all_members)
            group = get_scim_group(row, all_members, self.group_attr_map)
            all_groups.append(group)
            row = cursor.fetchone()
        conn.close()
        conn_member.close()
        return all_groups

    def format_record(self, row):
        row['FID'] = str(row.get('FID', ''))
        row['FFULL_NAME'] = row.get('FFULL_NAME', '').strip()
        if 'FCOMP' in row:
            row['FCOMP_ID'] = row.get('FCOMP')
        if 'COMPNAME' in row:
            row['FCOMP'] = row.get('COMPNAME', '')
        group_manager = row.get('FMANAGER')
        manager_fcode = ''
        if group_manager:
            if ':' in group_manager:
                manager_fcode = group_manager.split(':')[0]
            elif '：' in group_manager:
                manager_fcode = group_manager.split('：')[0]
            else:
                manager_fcode = ''
            row['FMANAGER'] = manager_fcode
        return row

    def create_async2(self, resource, correlation_identifier):
        raise NotImplementedException('Not implemented')

    def delete_async2(self, resource_identifier, correlation_identifier):
        raise NotImplementedException('Not implemented')

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
            groups = self.get_db_groups()
            return groups

        query_filter = parameters.alternate_filters[0]
        if not query_filter.attribute_path:
            raise ArgumentException('invalid parameters')
        if not query_filter.comparison_value:
            raise ArgumentException('invalid parameters')
        if query_filter.filter_operator != ComparisonOperator.Equals:
            raise NotSupportedException('unsupported comparison operator')

        if query_filter.attribute_path == AttributeNames.DisplayName:
            conn = get_connection(self.db_config)
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
        raise NotImplementedException('Not implemented')

    def retrieve_async2(self, parameters, correlation_identifier):
        if not parameters:
            raise ArgumentNullException('parameters')
        if not correlation_identifier:
            raise ArgumentNullException('correlation_identifier')
        if not parameters.resource_identifier.identifier:
            raise ArgumentNullException('parameters')

        dept_table = self.db_config.get('dept_table')
        company_table = self.db_config.get('company_table')
        identifier = parameters.resource_identifier.identifier
        conn = get_connection(self.db_config)
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
        raise NotImplementedException

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
        manager_fcode = ''
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

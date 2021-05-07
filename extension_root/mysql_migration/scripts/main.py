#!/usr/bin/env python3
import uuid
import json
import pathlib
import collections
import datetime
import logging
import MySQLdb
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 1: 同步用户，每同步一条用户记录，记录v1.user.id-->v2.user.uuid的映射
# 方便后面同步用户和其他表的关系时根据uuid取到v2中对应的用户
# (组，权限，应用v1中都有uuid字段, 用户没有)
def sync_common(cursor1, cursor2, table_map, column_map, extra_cols=[], get_extra=None):
    v1_table = table_map[0]
    v2_table = table_map[1]
    v1_cols = []
    v2_cols = []
    for v1_col, v2_col in column_map.items():
        if v2_col:
            v1_cols.append(v1_col)
            v2_cols.append(v2_col)

    if extra_cols:
        v2_cols.extend((extra_cols))

    # 查询v1时，把id也带出来
    v1_cols.insert(0, 'id')
    v1_cols_str = ','.join(v1_cols)
    v2_cols_str = ','.join(v2_cols)
    v2_cols_percent = ','.join(['%s'] * len(v2_cols))
    v1_query_str = (
        f'select {v1_cols_str} from {v1_table} where is_del=0 order by id asc'
    )
    v2_insert_str = f'insert into {v2_table} ({v2_cols_str}) values ({v2_cols_percent})'
    cursor1.execute(v1_query_str)
    logger.info(f'<========= sync {table_map[0]} to {table_map[1]} start')
    counter = 0
    skipped = 0
    while True:
        row_data = cursor1.fetchone()
        if not row_data:
            break
        row_data = list(row_data)
        id = row_data.pop(0)
        extra_values = get_extra(id)
        row_data.extend(extra_values)
        row_data = tuple(row_data)
        try:
            cursor2.execute(v2_insert_str, row_data)
        except IntegrityError as e:
            logger.error(e)
            skipped += 1
            continue
        except Exception as e:
            raise e
        counter += 1
    logger.info(
        f'=========> Sync {table_map[0]} end, Total Synced: {counter}, Skipped: {skipped}'
    )


# admin 或者其他用户可能会存在用户名重复
def get_user_uuid(tenant_id, v1_id):
    from extension_root.mysql_migration.models import V1UserIdUUID

    res = V1UserIdUUID.objects.filter(tenant_id=tenant_id, v1_user_id=v1_id).first()
    if not res:
        uuid_str = uuid.uuid4().hex
        V1UserIdUUID.objects.create(
            tenant_id=tenant_id, v1_user_id=v1_id, v1_user_uuid=uuid_str
        )
        return uuid_str
    else:
        return res.v1_user_uuid.hex


def get_table_uuid(cursor1, table_name, table_id):
    cursor1.execute(f'select uuid from {table_name} where id = {table_id}')
    res = cursor1.fetchone()
    if res:
        return res[0]


def sync_user(tenant_id, v1_conn, v2_conn):
    cursor1 = v1_conn.cursor()
    cursor2 = v2_conn.cursor()
    from .user_map import user_table_map, user_column_map

    extra_cols = [
        'uuid',
        'is_superuser',
        'is_staff',
        'date_joined',
        'last_name',
        'nickname',
        'country',
        'city',
    ]

    # id_uuid_map = get_id_uuid_map(cursor1)

    def get_extra_values(v1_id, *args, **kwargs):
        # user_uuid = id_uuid_map.get(str(v1_id))
        user_uuid = get_user_uuid(tenant_id, v1_id)
        return [user_uuid, 0, 1, datetime.datetime.now(), '', '', '', '']

    sync_common(
        cursor1, cursor2, user_table_map, user_column_map, extra_cols, get_extra_values
    )

    v2_conn.commit()
    cursor1.close()
    cursor2.close()


# 2: 同步组(先同步非parent_id字段，再同步parent_id)
def sync_group(tenant_id, v1_conn, v2_conn):
    cursor1 = v1_conn.cursor()
    cursor2 = v2_conn.cursor()
    from .group_map import group_table_map, group_column_map

    extra_cols = ['tenant_id']

    def get_extra_values(v1_id, *args, **kwargs):
        return [tenant_id]

    sync_common(
        cursor1,
        cursor2,
        group_table_map,
        group_column_map,
        extra_cols,
        get_extra_values,
    )
    v2_conn.commit()
    cursor1.close()
    cursor2.close()


# 2.1 同步组和组的关系parent_id


def sync_group_parent(tenant_id, v1_conn, v2_conn):

    cursor1 = v1_conn.cursor()
    cursor2 = v2_conn.cursor()
    v1_query_str = """SELECT A.uuid,B.uuid from oneid_meta_group A left join oneid_meta_group B
                    on A.parent_id = B.id where A.is_del=0 and B.is_del=0"""
    cursor1.execute(v1_query_str)
    logger.info('<========= sync group parent_id start')
    counter = 0
    skipped = 0
    while True:
        row_data = cursor1.fetchone()
        if not row_data:
            break
        child_uuid = row_data[0]
        parent_uuid = row_data[1]

        v2_query_id = 'SELECT id from inventory_group where uuid = %s'

        cursor2.execute(v2_query_id, (parent_uuid,))
        res = cursor2.fetchone()
        if not res:
            logger.error(
                'parent_group: {} not found in v2 inventory_group'.format(parent_uuid)
            )
            skipped += 1
            continue
        v2_parent_id = res[0]

        v2_update_str = 'update inventory_group set parent_id = %s where uuid = %s'
        try:
            cursor2.execute(v2_update_str, (v2_parent_id, child_uuid))
        except IntegrityError as e:
            logger.error(e)
            skipped += 1
            continue
        except Exception as e:
            raise e
        counter += 1
    logger.info(
        f'=========> Sync group parent end, Total Synced: {counter}, Skipped: {skipped}'
    )
    v2_conn.commit()
    cursor1.close()
    cursor2.close()


# 3: 同步权限
def sync_perm(tenant_id, v1_conn, v2_conn):
    cursor1 = v1_conn.cursor()
    cursor2 = v2_conn.cursor()
    from .perm_map import perm_table_map, perm_column_map

    extra_cols = ['tenant_id', 'content_type_id']

    def get_extra_values(v1_id, *args, **kwargs):
        return [tenant_id, 1]

    sync_common(
        cursor1,
        cursor2,
        perm_table_map,
        perm_column_map,
        extra_cols,
        get_extra_values,
    )
    v2_conn.commit()
    cursor1.close()
    cursor2.close()


# 4: 同步应用
def sync_app(tenant_id, v1_conn, v2_conn):
    cursor1 = v1_conn.cursor()
    cursor2 = v2_conn.cursor()
    from .app_map import app_table_map, app_column_map

    extra_cols = ['tenant_id', 'url', 'type', 'data']

    def get_extra_values(v1_id, *args, **kwargs):
        return [tenant_id, '', '', '{}']

    sync_common(
        cursor1,
        cursor2,
        app_table_map,
        app_column_map,
        extra_cols,
        get_extra_values,
    )
    v2_conn.commit()
    cursor1.close()
    cursor2.close()


def _sync_many2many(
    tenant_id,
    v1_conn,
    v2_conn,
    v1_rela_tables,
    v1_cols,
    v2_rela_tables,
    v2_cols,
    sync_user=False,
):
    """
    A: v1_rela_tables[0] <-> B: v1_rela_tables[1] <-> C: v1_rela_tables[2]
                        v1_cols[0]:v1_cols[1]
    """
    cursor1 = v1_conn.cursor()
    cursor2 = v2_conn.cursor()

    v1_query_str = """SELECT B.{},C.uuid from {} B left join {} C
                      on B.{}  = C.id
                      where B.is_del=0 and C.is_del=0
                   """.format(
        v1_cols[0],
        v1_rela_tables[1],
        v1_rela_tables[2],
        v1_cols[1],
    )
    counter = 0
    skipped = 0

    def get_v2_table_id(cursor2, table_name, uuid_str):
        v2_id_query = f'SELECT id from {table_name} WHERE uuid = %s'
        cursor2.execute(v2_id_query, (uuid_str,))
        res = cursor2.fetchone()
        if not res:
            logger.error(f'No uuid:{uuid_str} found in V2: {table_name}')
            return None
        else:
            return res[0]

    cursor1.execute(v1_query_str)
    while True:
        row_data = cursor1.fetchone()
        if not row_data:
            break
        if sync_user:
            v1_col1_uuid = get_user_uuid(tenant_id, row_data[0])
        else:
            v1_col1_uuid = get_table_uuid(cursor1, v1_rela_tables[0], row_data[0])
        v1_col2_uuid = row_data[1]

        v2_table1_id = get_v2_table_id(cursor2, v2_rela_tables[0], v1_col1_uuid)
        if not v2_table1_id:
            skipped += 1
            continue

        v2_table2_id = get_v2_table_id(cursor2, v2_rela_tables[2], v1_col2_uuid)
        if not v2_table2_id:
            skipped += 1
            continue

        v2_insert = f'insert into {v2_rela_tables[1]} ({v2_cols[0]}, {v2_cols[1]}) values (%s, %s)'

        try:
            cursor2.execute(v2_insert, (v2_table1_id, v2_table2_id))
        except IntegrityError as e:
            logger.error(e)
            skipped += 1
            continue
        except Exception as e:
            raise e
        counter += 1

    v2_conn.commit()
    cursor1.close()
    cursor2.close()
    return counter, skipped


# 5: 同步用户和组的关系
def sync_user_group_relation(tenant_id, v1_conn, v2_conn):
    logger.info('<========= sync user group relation start')
    v1_rela_tables = ('oneid_meta_user', 'oneid_meta_groupmember', 'oneid_meta_group')
    v1_cols = ('user_id', 'owner_id')
    v2_rela_tables = ('inventory_user', 'inventory_user_groups', 'inventory_group')
    v2_cols = ('user_id', 'group_id')
    counter, skipped = _sync_many2many(
        tenant_id,
        v1_conn,
        v2_conn,
        v1_rela_tables,
        v1_cols,
        v2_rela_tables,
        v2_cols,
        sync_user=True,
    )

    logger.info(
        f'=========> Sync user group end, Total Synced: {counter}, Skipped: {skipped}'
    )


# 6: 同步用户和权限的关系
# {"oneid_meta_userperm": "inventory_user_user_permissions"}
# {"perm_id": "permission_id", "owner_id": "user_id"}
def sync_user_perm_relation(tenant_id, v1_conn, v2_conn):
    logger.info('<========= sync user perm relation start')
    v1_rela_tables = ('oneid_meta_user', 'oneid_meta_userperm', 'oneid_meta_perm')
    v1_cols = ('owner_id', 'perm_id')
    v2_rela_tables = (
        'inventory_user',
        'inventory_user_user_permissions',
        'inventory_permission',
    )
    v2_cols = ('user_id', 'permission_id')
    counter, skipped = _sync_many2many(
        tenant_id,
        v1_conn,
        v2_conn,
        v1_rela_tables,
        v1_cols,
        v2_rela_tables,
        v2_cols,
        sync_user=True,
    )

    logger.info(
        f'=========> Sync user perm end, Total Synced: {counter}, Skipped: {skipped}'
    )


# 7: 同步组和权限的关系
# {"oneid_meta_groupperm": "inventory_group_permissions"}
# {"perm_id": "permission_id", "owner_id": "group_id"}
def sync_group_perm_relation(tenant_id, v1_conn, v2_conn):
    logger.info('<========= sync group perm relation start')
    v1_rela_tables = ('oneid_meta_group', 'oneid_meta_groupperm', 'oneid_meta_perm')
    v1_cols = ('owner_id', 'perm_id')
    v2_rela_tables = (
        'inventory_group',
        'inventory_group_permissions',
        'inventory_permission',
    )
    v2_cols = ('group_id', 'permission_id')
    counter, skipped = _sync_many2many(
        tenant_id,
        v1_conn,
        v2_conn,
        v1_rela_tables,
        v1_cols,
        v2_rela_tables,
        v2_cols,
        sync_user=False,
    )

    logger.info(
        f'=========> Sync group perm end, Total Synced: {counter}, Skipped: {skipped}'
    )


# 8: 同步用户和租户的关系
def sync_user_tenant_relation(tenant_id, v1_conn, v2_conn):
    from extension_root.mysql_migration.models import V1UserIdUUID

    cursor2 = v2_conn.cursor()

    logger.info('<========= sync user tenant relation start')
    counter = 0
    skipped = 0

    res = V1UserIdUUID.objects.filter(tenant_id=tenant_id).value_list(
        'v1_user_id', 'v1_user_uuid'
    )
    for user_id, user_uuid in res:
        v2_query_str = 'SELECT id from inventory_user where uuid = %s'
        cursor2.execute(v2_query_str, (user_uuid,))
        res = cursor2.fetchone()
        if not res:
            logger.error('No user_uuid:{} found in V2 DB'.format(user_uuid))
            skipped += 1
            continue
        v2_user_id = res[0]
        v2_insert = (
            'insert into inventory_user_tenants (user_id, tenant_id) values (%s, %s)'
        )
        cursor2.execute(v2_insert, (v2_user_id, tenant_id))
        counter += 1

    logger.info(
        f'=========> Sync user tenant end, Total Synced: {counter}, Skipped: {skipped}'
    )
    v2_conn.commit()
    cursor2.close()


def get_v2_tenant_id(v2_conn, tenant_uuid):
    cursor2 = v2_conn.cursor()
    cursor2.execute('SELECT id from tenant_tenant where uuid = %s', (tenant_uuid,))
    result = cursor2.fetchone()
    if not result:
        cursor2.close()
        return
    tenant_id = result[0]
    cursor2.close()
    return tenant_id


def migrate(v1_conn, v2_conn, tenant_uuid):
    tenant_id = get_v2_tenant_id(v2_conn, tenant_uuid)
    if not tenant_id:
        logger.error('No tenant found!')
        return False
    logger.info('Tenant ID: {}'.format(tenant_id))
    sync_user(tenant_id, v1_conn, v2_conn)
    sync_group(tenant_id, v1_conn, v2_conn)
    sync_group_parent(tenant_id, v1_conn, v2_conn)
    sync_perm(tenant_id, v1_conn, v2_conn)
    sync_app(tenant_id, v1_conn, v2_conn)
    sync_user_group_relation(tenant_id, v1_conn, v2_conn)
    sync_user_perm_relation(tenant_id, v1_conn, v2_conn)
    sync_group_perm_relation(tenant_id, v1_conn, v2_conn)
    sync_user_tenant_relation(tenant_id, v1_conn, v2_conn)

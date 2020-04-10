'''
修改django测试模块创建数据库部分
'''
from test.utils.test_data_manager import SqliteToSqlManager
from django.test.utils import get_unique_databases_and_mirrors, connections


def setup_databases(verbosity, keepdb=False, debug_sql=False, parallel=0, **kwargs):    # pylint: disable=too-many-locals, unused-argument
    """Create the test databases."""
    test_databases, mirrored_aliases = get_unique_databases_and_mirrors()
    old_names = []

    for _, (db_name, aliases) in test_databases.items():
        first_alias = None
        for alias in aliases:
            connection = connections[alias]
            old_names.append((connection, db_name, first_alias is None))

            # Actually create the database for the first connection
            if first_alias is None:
                first_alias = alias
                # ---以下是修改部分---
                SqliteToSqlManager().write_sql_to_test_db()
                # ---以上是修改部分---
                if parallel > 1:
                    for index in range(parallel):
                        connection.creation.clone_test_db(
                            suffix=str(index + 1),
                            verbosity=verbosity,
                            keepdb=keepdb,
                        )
            # Configure all other connections as mirrors of the first one
            else:
                connections[alias].creation.set_as_test_mirror(connections[first_alias].settings_dict)

    # Configure the test mirrors.
    for alias, mirror_alias in mirrored_aliases.items():
        connections[alias].creation.set_as_test_mirror(connections[mirror_alias].settings_dict)

    if debug_sql:
        for alias in connections:
            connections[alias].force_debug_cursor = True

    return old_names

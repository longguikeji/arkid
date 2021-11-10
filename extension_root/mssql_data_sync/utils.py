from data_sync.models import DataSyncConfig
import pymssql


def load_config(tenant_uuid):
    config = DataSyncConfig.active_objects.filter(
        tenant__uuid=tenant_uuid,
        type="mssql_data_sync",
    ).first()

    if not config:
        return None
    return config


def get_connection(db_config):
    conn = pymssql.connect(
        db_config.get('server'),
        db_config.get('user'),
        db_config.get('password'),
        db_config.get('database'),
        port=db_config.get('port')
    )
    return conn

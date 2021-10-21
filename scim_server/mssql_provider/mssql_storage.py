#!/usr/bin/env python3
import pymssql
from config import get_app_config


class MssqlConfig:
    def __init__(self, server, user, password, database, port='1433'):
        self.server = server
        self.user = user
        self.password = password
        self.database = database
        if not port:
            self.port = '1433'
        else:
            self.port = port

    def get_connection(self):
        conn = pymssql.connect(self.server, self.user, self.password, self.database)
        return conn


def get_mssql_config():
    config = get_app_config()
    mssql_config = config.data.get('mssql')
    if not mssql_config:
        return None
    server = mssql_config.get('server')
    user = mssql_config.get('user')
    password = mssql_config.get('password')
    database= mssql_config.get('database')
    port = mssql_config.get('port')
    db_config = MssqlConfig(
        server, user, password, database, port=port
    )
    return db_config

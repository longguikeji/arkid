from typing import Any
from common.provider import MigrationProvider
from pathlib import Path
import uuid
import oss2
import os
import MySQLdb
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS, load_backend
from .scripts import main


class MysqlMigrationProvider(MigrationProvider):
    def __init__(self, host: str, port: str, user: str, passwd: str, db: str) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db

    def migrate(self, tenant_uuid):
        v1_conn = self.ensure_connection()
        if not v1_conn:
            return False
        v2_conn = self.create_connection()
        try:
            main.migrate(v1_conn, v2_conn, tenant_uuid)
        except Exception as e:
            print(e)
        finally:
            v1_conn.close()
            v2_conn.close()

    def ensure_connection(self):
        try:
            conn = MySQLdb.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                passwd=self.passwd,
                db=self.db,
                charset='utf8',
            )
        except Exception as e:
            print(e)
            return None
        return conn

    def create_connection(self, alias=DEFAULT_DB_ALIAS):
        connections.ensure_defaults(alias)
        connections.prepare_test_settings(alias)
        db = connections.databases[alias]
        backend = load_backend(db['ENGINE'])
        return backend.DatabaseWrapper(db, alias)

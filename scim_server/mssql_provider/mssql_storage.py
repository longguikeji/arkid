#!/usr/bin/env python3
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
        self.emp_table = 'EMP'
        self.dept_table = 'DEPT'
        self.job_table = 'JOB'
        self.company_table = 'ECOMPANY'

    def get_connection(self):
        import pymssql
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
    database = mssql_config.get('database')
    port = mssql_config.get('port')
    db_config = MssqlConfig(server, user, password, database, port=port)

    emp_table = mssql_config.get('emp_table')
    if emp_table:
        db_config.emp_table = emp_table

    dept_table = mssql_config.get('dept_table')
    if dept_table:
        db_config.dept_table = dept_table

    job_table = mssql_config.get('job_table')
    if job_table:
        db_config.job_table = job_table

    company_table = mssql_config.get('company_table')
    if company_table:
        db_config.company_table = company_table

    return db_config

'''
数据导入导出函数
'''
import os
import re
import pathlib
import time
import sqlite3
import sys
import getopt
import logging

TABLE_NAMES = [
    'auth_group',
    'oneid_meta_deptmember',
    'auth_group_permissions',
    'oneid_meta_deptperm',
    'auth_permission',
    'oneid_meta_dingconfig',
    'auth_user',
    'oneid_meta_dingdept',
    'auth_user_groups',
    'oneid_meta_dinggroup',
    'auth_user_user_permissions',
    'oneid_meta_dinguser',
    'authtoken_token',
    'oneid_meta_emailconfig',
    'captcha_captchastore',
    'oneid_meta_group',
    'corsheaders_corsmodel',
    'oneid_meta_groupmember',
    'django_admin_log',
    'oneid_meta_groupperm',
    'django_celery_beat_crontabschedule',
    'oneid_meta_httpapp',
    'django_celery_beat_intervalschedule',
    'oneid_meta_invitation',
    'django_celery_beat_periodictask',
    'oneid_meta_ldapapp',
    'django_celery_beat_periodictasks',
    'oneid_meta_log',
    'django_celery_beat_solarschedule',
    'oneid_meta_managergroup',
    'django_celery_results_taskresult',
    'oneid_meta_minioconfig',
    'django_content_type',
    'oneid_meta_nativefield',
    # 'django_migrations',
    'oneid_meta_perm',
    'django_session',
    'oneid_meta_posixuser',
    'django_site',
    'oneid_meta_qqconfig',
    'drf_expiring_authtoken_expiringtoken',
    'oneid_meta_qquser',
    'oauth2_provider_accesstoken',
    'oneid_meta_requestaccesslog',
    'oauth2_provider_application',
    'oneid_meta_requestdataclientlog',
    'oauth2_provider_grant',
    'oneid_meta_smsconfig',
    'oauth2_provider_refreshtoken',
    'oneid_meta_storageconfig',
    'oneid_meta_accountconfig',
    'oneid_meta_subaccount',
    'oneid_meta_alipayconfig',
    'oneid_meta_user',
    'oneid_meta_alipayuser',
    'oneid_meta_userperm',
    'oneid_meta_app',
    'oneid_meta_wechatconfig',
    'oneid_meta_companyconfig',
    'oneid_meta_wechatuser',
    'oneid_meta_customfield',
    'oneid_meta_workwechatconfig',
    'oneid_meta_customuser',
    'oneid_meta_workwechatuser',
    'oneid_meta_dept',
]

log = logging.getLogger(__name__)    # pylint: disable=invalid-name

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SqliteToSqlManager:
    '''测试数据库unittest.sqlite3导入sql文件
    '''
    base_path = pathlib.Path(BASE_DIR)
    DATASET_SQL_PATH = base_path / 'test' / 'data' / 'test.sql'

    def __init__(self):
        self.conn = sqlite3.connect(BASE_DIR + '/test/data/unittest.sqlite3')
        self.cur = self.conn.cursor()

    def write_sql_to_test_db(self):    # pylint: disable=no-self-use
        '''sql写入测试数据库
        '''
        try:
            self.cur.execute('DELETE FROM sqlite_sequence')
            self.conn.commit()
        except Exception as err:    # pylint: disable=broad-except
            log.info(err)

        with open(self.DATASET_SQL_PATH, 'r') as f:
            count = len(f.readlines())
            f.seek(0)
            for _ in range(count):
                try:
                    self.cur.executescript(f.readline())
                except Exception as err:    # pylint: disable=broad-except
                    log.info(err)
            self.conn.commit()
            self.conn.close()


class DBManager:
    '''备份项目数据库为sql文件;sql文件导入项目数据库
    '''
    base_path = pathlib.Path(BASE_DIR)
    ORIGIN_DB_PATH = base_path / 'db' / 'db.sqlite3'
    DATASET_SQL_PATH = base_path / 'test' / 'data' / 'test.sql'

    def __init__(self):
        self.conn = sqlite3.connect(BASE_DIR + '/db/db.sqlite3')
        self.cur = self.conn.cursor()

    def load_test_db(self):    # pylint: disable=no-self-use
        '''
        将测试数据放入项目操作数据库文件夹进行修改
        '''
        for table in TABLE_NAMES:
            self.cur.execute('DELETE FROM %s' % table)
            self.cur.execute('DELETE FROM sqlite_sequence WHERE name = "%s";' % table)

        with open(self.DATASET_SQL_PATH, 'r') as f:
            count = len(f.readlines())
            f.seek(0)
            for _ in range(count):
                try:
                    self.cur.executescript(f.readline())
                except Exception as err:    # pylint: disable=broad-except
                    log.info(err)
            self.conn.commit()
            self.conn.close()

    def update_test_sql(self):
        '''
        转换数据库为sql文件
        '''
        base_path = pathlib.Path(BASE_DIR)
        save_sql_name = 'test_%s.sql' % (time.strftime('%Y-%m-%d_%H:%M:%S'))
        save_sql_path = base_path / 'test' / 'data' / save_sql_name
        if os.path.exists(self.DATASET_SQL_PATH):
            os.rename(self.DATASET_SQL_PATH, save_sql_path)

        try:
            con = sqlite3.connect(BASE_DIR + '/db/db.sqlite3')
            with open(BASE_DIR + '/test/data/test.sql', 'w+') as f:
                for line in con.iterdump():
                    if len(re.findall(r'django_migrations', line)) > 0:
                        continue
                    f.write('%s\n' % line)
            con.close()
        except Exception as err:    # pylint: disable=broad-except
            log.info(err)


def main(argv):
    '''识别参数执行命令
    '''
    try:
        opts, _ = getopt.getopt(argv, "hld")
    except getopt.GetoptError:
        print('Error: test_data_manager.py -l')
        print('Error: test_data_manager.py -d')
        sys.exit(2)

    for opt, _ in opts:
        if opt == "-h":
            print('test_data_manager.py -l/-load "(load)将test.sql导入db.sqlite3')
            print('test_data_manager.py -d/-dump "(dump)将db.sqlite3导出test.sql')
        elif opt in ("-l", "-load"):
            manager = DBManager()    # pylint: disable=invalid-name
            manager.load_test_db()
        elif opt in ("-d", "-dump"):
            manager = DBManager()
            manager.update_test_sql()


if __name__ == "__main__":
    main(sys.argv[1:])

'''
数据导入导出函数
'''
import os
import shutil
import pathlib
import time
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SqliteToSqlManager:
    '''
    sqliet3转换sql文件管理器
    '''
    base_path = pathlib.Path(BASE_DIR)
    ORIGIN_DB_PATH = base_path / 'db' / 'db.sqlite3'
    DATASET_DB_PATH = base_path / 'test' / 'data' / 'dataset.sqlite3'
    DATASET_SQL_PATH = base_path / 'test' / 'data' / 'test.sql'

    def __init__(self):
        self.conn = sqlite3.connect(BASE_DIR + '/db/db.sqlite3')
        self.cur = self.conn.cursor()

    def write_sql_to_test_db(self):    # pylint: disable=no-self-use
        '''
        sql写入测试数据库
        '''

        base_path = pathlib.Path(BASE_DIR)
        new_db_name = 'db_%s.sqlite3' % (time.strftime('%Y-%m-%d_%H:%M:%S'))
        new_db_path = base_path / 'db' / new_db_name
        # os.rename(self.ORIGIN_DB_PATH, new_db_path)
        shutil.copy2(self.ORIGIN_DB_PATH, new_db_path)

        try:
            self.cur.execute('DELETE FROM sqlite_sequence')
            self.conn.commit()

        except Exception as err:    # pylint: disable=broad-except
            print(err)

        with open(self.DATASET_SQL_PATH, 'r') as f:
            count = len(f.readlines())
            f.seek(0)
            for _ in range(count):
                try:
                    self.cur.executescript(f.readline())
                except Exception:    # pylint: disable=broad-except
                    pass
            self.conn.commit()
            self.conn.close()

    def update_test_sql(self):    # pylint: disable=no-self-use
        '''
        转换数据库为sql文件
        '''
        try:
            con = sqlite3.connect(BASE_DIR + '/db/db.sqlite3')
            with open(BASE_DIR + '/test/data/test.sql', 'w') as f:
                for line in con.iterdump():
                    f.write('%s\n' % line)
            con.close()
        except Exception as err:    # pylint: disable=broad-except
            return err

'''
修改django测试模块数据库配置
'''
from test.utils.setup_databases import setup_databases as _setup_databases
from django.test.runner import DiscoverRunner


class TestDiscoverRunner(DiscoverRunner):
    """A Django test runner that uses unittest2 test discovery."""
    def setup_databases(self, **kwargs):
        return _setup_databases(self.verbosity, self.keepdb, self.debug_sql, self.parallel, **kwargs)

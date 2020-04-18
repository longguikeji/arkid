import os
import re
from sys import _getframe
from django.conf import settings


def get_top_level_dirname() -> str:
    """
    获取ArkID打包所用顶层文件夹名称.
    :return:
    """
    path, _ = os.path.split(_getframe().f_code.co_filename)
    path, _ = os.path.split(path)
    _, dirname = os.path.split(path)
    if re.search(r"\W", dirname):
        raise Exception('解析到的目录未按预期工作，请检查项目主目录名称的规范性.')
    return dirname


def validate_attr(file_name, func_name, f_lineno, *arg):
    """
    检查ArkID必需参数，是否存在于用户的项目配置文件中.
    """
    for attr in arg:
        if not hasattr(settings, attr):
            msg = 'file:{0} func:{1} lineno:{2}'.format(file_name, func_name, f_lineno)
            raise NotConfiguredException(msg)


class NotConfiguredException(Exception):
    """
    ArkID作为第三方应用导入Django时，用户未进行必要的配置.
    """

    def __init__(self, *args, **kwargs):  # real signature unknown
        reminder = '\nArkID 中存在参数未进行显式配置,可参照 {0} 下的 {1} 默认配置文件进行操作.未配置参数路径为:\n'.format(os.path.join(get_top_level_dirname(), 'oneid'), 'settings_setup.py')
        for item in args:
            reminder = '{0}{1}\n'.format(reminder, item)
        self.args = (reminder, )



VERSION = (0, 1, 0, 'final', 0)
__title__ = 'arkid-client'
__version_info__ = VERSION
__version__ = '.'.join(map(
    str, VERSION[:3])) + ('-{}{}'.format(VERSION[3], VERSION[4] or '') if VERSION[3] != 'final' else '')
__author__ = 'LongGuiKeJi'
__license__ = 'GNU'
__copyright__ = 'Copyright 2018-2020 LongGuiKeJi'

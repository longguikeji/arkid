from .extension import MysqlStatisticsExtension


extension = MysqlStatisticsExtension(
    scope='global',
    type='global',
    name='mysql_statistics',
    tags='statistics',
    description='Mysql statistics provider',
    version='1.0',
    homepage='https://www.longguikeji.com',
    logo='',
    maintainer='louis.law@hotmail.com',
)

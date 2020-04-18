from sys import _getframe

from django.db import migrations, models
from django.conf import settings

from ...common.setup_utils import NotConfiguredException, validate_attr


def create_buildin_perm(apps, schema_editor):
    '''
    创建内置权限
    '''
    Perm = apps.get_model('oneid_meta', 'Perm')

    perm, _ = Perm.objects.get_or_create(
        subject='system',
        scope='log',
        action='read',
        uid='system_log_read',
    )
    perm.name = '查看日志'
    perm.save()

    perm, _ = Perm.objects.get_or_create(
        subject='system',
        scope='config',
        action='write',
        uid='system_config_write',
    )
    perm.name = '公司配置、基础设施配置'
    perm.save()

    perm, _ = Perm.objects.get_or_create(
        subject='system',
        scope='account',
        action='sync',
        uid='system_account_sync',
    )
    perm.name = '账号同步'
    perm.save()



class Migration(migrations.Migration):


    dependencies = [
        ('oneid_meta', '0049_httpapp_ldapapp'),
    ]

    operations = []
    validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno, 'TESTING')

    if not settings.TESTING:
        operations += [
            migrations.RunPython(create_buildin_perm)
        ]

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
        scope='user',
        action='create',
        uid='system_user_create',
    )
    perm.name = '创建用户'
    perm.save()

    perm, _ = Perm.objects.get_or_create(
        subject='system',
        scope='category',
        action='create',
        uid='system_category_create',
    )
    perm.name = '创建大类'
    perm.save()

    perm, _ = Perm.objects.get_or_create(
        subject='system',
        scope='app',
        action='create',
        uid='system_app_create',
    )
    perm.name = '创建应用'
    perm.save()



class Migration(migrations.Migration):


    dependencies = [
        ('oneid_meta', '0044_auto_20190722_1226'),
    ]

    operations = []

    validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno, 'TESTING')

    if not settings.TESTING:
        operations += [
            migrations.RunPython(create_buildin_perm)
        ]

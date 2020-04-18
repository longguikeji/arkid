from sys import _getframe

from django.db import migrations, models
from django.conf import settings

from ...common.setup_utils import NotConfiguredException, validate_attr


def register_noah_admin(apps, schema_editor):
    '''
    将noah管理后台注册为一个APP

    同时删除原ark-meta-server
    其access权限，认为所有人都拥有
    其system_ark-meta-server_all权限，被 app_noah-admin_access替换
    '''
    APP = apps.get_model('oneid_meta', 'APP')
    Perm = apps.get_model('oneid_meta', 'Perm')
    app, _ = APP.objects.get_or_create(
        uid='noah-admin',
        name='noah管理后台',
        remark='服务器管理、应用管理等功能',
        editable=False,
    )
    uid = f'app_{app.uid}_access'
    if not Perm.objects.filter(uid=uid).exists():
        Perm.objects.create(uid=uid, name=f'访问{app.name}', subject='app', scope=app.uid, action='access')

    ark_meta_server = APP.objects.filter(uid='ark-meta-server').first()
    if ark_meta_server:
        ark_meta_server.delete()


def register_arker_editor(apps, schema_editor):
    '''
    将AE注册为一个APP
    '''
    APP = apps.get_model('oneid_meta', 'APP')
    Perm = apps.get_model('oneid_meta', 'Perm')
    app, _ = APP.objects.get_or_create(
        uid='arker-editor',
        name='Arker编辑器',
        remark='Arker编辑、发布、导出等功能',
        editable=False,
    )
    uid = f'app_{app.uid}_access'
    if not Perm.objects.filter(uid=uid).exists():
        Perm.objects.create(uid=uid, name=f'访问{app.name}', subject='app', scope=app.uid, action='access')

class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0024_register_arkbe'),
    ]

    validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno, 'TESTING')

    if not settings.TESTING:
        operations = [
            migrations.RunPython(register_noah_admin),
            migrations.RunPython(register_arker_editor),
        ]

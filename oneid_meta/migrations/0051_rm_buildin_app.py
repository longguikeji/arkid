from sys import _getframe

from django.db import migrations, models
from django.conf import settings

from ...common.setup_utils import NotConfiguredException, validate_attr


def delete_buildin_app(apps, schema_editor):
    '''
    删除内置应用
    '''
    APP = apps.get_model('oneid_meta', 'APP')

    noah_admin = APP.objects.filter(uid='noah-admin').first()
    if noah_admin:
        noah_admin.delete()

    ae = APP.objects.filter(uid='arker-editor').first()
    if ae:
        ae.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0050_add_buildin_perm'),
    ]

    operations = []
    validate_attr(_getframe().f_code.co_filename, _getframe().f_code.co_name, _getframe().f_lineno, 'TESTING')

    if not settings.TESTING:
        operations += [
            migrations.RunPython(delete_buildin_app)
        ]

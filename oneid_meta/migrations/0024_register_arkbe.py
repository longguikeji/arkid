
from django.db import migrations, models

ARKBE_ADMIN_PERM = 'system_ark-meta-server_all'


def register_arkbe(apps, schema_editor):
    '''
    将arkbe注册为一个APP
    '''
    APP = apps.get_model('oneid_meta', 'APP')
    APP.objects.create(
        uid='ark-meta-server',
        name='arkbe',
        remark='',
        editable=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0023_auto_20190425_1232'),
    ]

    operations = [
        migrations.RunPython(register_arkbe),
    ]

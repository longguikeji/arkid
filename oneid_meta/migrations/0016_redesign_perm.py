
from django.db import migrations, models

ADMIN_ACCESS_PERM = 'system_oneid_all'


def register_oneid_self(apps, schema_editor):
    APP = apps.get_model('oneid_meta', 'APP')
    APP.objects.create(
        uid='oneid',
        name='OneID',
        remark='',
        editable=False,
    )


def reset_default_perms(apps, schema_editor):
    '''
    重置目前默认权限的新增字段
    '''
    Perm = apps.get_model('oneid_meta', 'Perm')
    for perm_uid in [
        'system_oneid_all',  # deprecated
        'system_ark-meta-server_all',
    ]:
        perm = Perm.objects.filter(uid=perm_uid).first()
        subject, scope, action = perm_uid.split('_')
        data = {
            'subject': subject,
            'scope': scope,
            'action': action,
            'editable': False,
            'default_value': False,
        }
        if not perm:
            perm = Perm.objects.create(**data)
        else:
            perm.__dict__.update(**data)
            perm.save()


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0015_auto_20190227_0038'),
    ]

    operations = [
        migrations.RunPython(register_oneid_self),
        migrations.RunPython(reset_default_perms),
    ]


from django.db import migrations, models

ARK_ALL_PERM = 'system_ark-meta-server_all'


def creata_perm_ark_all(apps, schema_editor):
    '''
    创建权限：访问ark-meta-server所有接口
    '''
    from ...oneid_meta.models import Perm

    Perm = apps.get_model('oneid_meta', 'Perm')

    perm = Perm.objects.create(
        uid=ARK_ALL_PERM,
        name='访问ark-meta-server所有接口',
        scope='ark-meta-server',
        action='all',
        subject='system',
    )


def assign_admin_with_perm_ark_all(apps, schema_editor):
    '''
    为管理员分配访问ark-meta-server所有接口的权限
    '''
    from ...oneid_meta.models import User, UserPerm, Perm
    User = apps.get_model('oneid_meta', 'User')
    UserPerm = apps.get_model('oneid_meta', 'UserPerm')
    Perm = apps.get_model('oneid_meta', 'Perm')
    admin = User.objects.get(username='admin')
    UserPerm.objects.create(
        owner=admin,
        perm=Perm.objects.get(uid=ARK_ALL_PERM),
        status=1,
        value=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0012_create_admin'),
    ]

    operations = [
        migrations.RunPython(creata_perm_ark_all),
        migrations.RunPython(assign_admin_with_perm_ark_all),
    ]

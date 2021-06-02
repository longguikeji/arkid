
from django.db import migrations, models
from django.conf import settings
from executer.utils.password import encrypt_password


ADMIN_ACCESS_PERM = 'system_oneid_all'


def creata_perm_oneid_all(apps, schema_editor):
    '''
    创建权限：登录后台
    '''
    Perm = apps.get_model('oneid_meta', 'Perm')
    Perm.objects.create(
        uid=ADMIN_ACCESS_PERM,
        name='OneID所有接口',
        scope='oneid',
        action='all',
        subject='system',
    )


def create_admin_user(apps, schema_editor):
    '''
    创建管理员
    '''
    User = apps.get_model('oneid_meta', 'User')
    UserPerm = apps.get_model('oneid_meta', 'UserPerm')
    Perm = apps.get_model('oneid_meta', 'Perm')
    admin = User.objects.create(
        username='admin',
        password=encrypt_password(settings.WEB_ADMIN_PASSWORD, settings.PASSWORD_ENCRYPTION),
    )
    UserPerm.objects.create(
        owner=admin,
        perm=Perm.objects.get(uid=ADMIN_ACCESS_PERM),
        status=1,
        value=True,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0011_perm_subject'),
    ]

    operations = [
        migrations.RunPython(creata_perm_oneid_all),
        migrations.RunPython(create_admin_user),
    ]

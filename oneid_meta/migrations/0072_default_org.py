from uuid import uuid4
from django.db import migrations, models
from django.conf import settings

def create_default_org(apps, schema_editor):
    '''
    创建默认组织
    '''

    Org = apps.get_model('oneid_meta', 'Org')
    User = apps.get_model('oneid_meta', 'User')
    Dept = apps.get_model('oneid_meta', 'Dept')
    Group = apps.get_model('oneid_meta', 'Group')
    GroupMember = apps.get_model('oneid_meta', 'GroupMember')

    name = '默认组织'
    user = User.objects.filter(username='admin').first()
    dept_root, _ = Dept.objects.get_or_create(uid='root')
    group_root, _ = Group.objects.get_or_create(uid='root')


    dept = Dept.objects.create(uid=uuid4(), name=name, parent=dept_root)
    group = Group.objects.create(uid=uuid4(), name=name, parent=group_root)
    direct = Group.objects.create(uid=uuid4(), name=f'{name}-无分组成员', parent=group)
    manager = Group.objects.create(uid=uuid4(), name=f'{name}-管理员', parent=group)
    role = Group.objects.create(uid=uuid4(), name=f'{name}-角色', parent=group)
    label = Group.objects.create(uid=uuid4(), name=f'{name}-标签', parent=group)

    GroupMember.objects.create(user=user, owner=direct)
    Org.objects.create(uuid='00000000-00000000-00000000-00000000',
                       name=name,
                       owner=user,
                       dept=dept,
                       group=group,
                       direct=direct,
                       manager=manager,
                       role=role,
                       label=label)

def go(*args):
    if not settings.TESTING:
        create_default_org(*args)


class Migration(migrations.Migration):
    dependencies = [
        ('oneid_meta', '0071_log_org'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name = 'user',
            managers = [ ('objects', models.manager.Manager()) ]
        ),
        migrations.RunPython(go),
    ]

from uuid import uuid4
from django.db import migrations, models
from django.conf import settings

def migrate(apps, schema_editor):
    '''
    migrate with a default organization
    '''

    APP = apps.get_model('oneid_meta', 'APP')
    Log = apps.get_model('oneid_meta', 'Log')
    Org = apps.get_model('oneid_meta', 'Org')
    User = apps.get_model('oneid_meta', 'User')
    Dept = apps.get_model('oneid_meta', 'Dept')
    Group = apps.get_model('oneid_meta', 'Group')
    UserPerm = apps.get_model('oneid_meta', 'UserPerm')
    OrgMember = apps.get_model('oneid_meta', 'OrgMember')
    GroupMember = apps.get_model('oneid_meta', 'GroupMember')
    CustomField = apps.get_model('oneid_meta', 'CustomField')
    CompanyConfig = apps.get_model('oneid_meta', 'CompanyConfig')

    config = CompanyConfig.objects.all().first()
    name = config.fullname_cn
    owner = None
    for user in User.objects.filter().all():
        if user.is_boss or user.username == 'admin'\
                or UserPerm.objects.filter(owner=user, perm__uid='system_oneid_all', value=True).exists():
            owner = user
            break

    dept_root = Dept.objects.filter(uid='root').first()
    group_root = Group.objects.filter(uid='root').first()

    dept = Dept.objects.create(uid=uuid4(), name=name, parent=dept_root)
    group = Group.objects.create(uid=uuid4(), name=name, parent=group_root)
    direct = Group.objects.create(uid=uuid4(), name=f'{name}-无分组成员', parent=group)
    manager = Group.objects.create(uid=uuid4(), name=f'{name}-管理员', parent=group)
    role = Group.objects.create(uid=uuid4(), name=f'{name}-角色', parent=group)
    label = Group.objects.create(uid=uuid4(), name=f'{name}-标签', parent=group)

    group.top = group.uid
    group.save()
    direct.top = direct.uid
    direct.save()
    manager.top = manager.uid
    manager.save()
    role.top = role.uid
    role.save()
    label.top = label.uid
    label.save()

    kw = {
        'uuid': uuid4(),
        'name': name,
        'owner': owner,
        'dept': dept,
        'group': group,
        'direct': direct,
        'manager': manager,
        'role': role,
        'label': label,
    }
    org = Org.objects.create(**kw)

    config.org = org
    config.save()
    for app in APP.objects.all():
        app.owner = org
        app.save()
    for log in Log.objects.all():
        log.org = org
        log.save()
    for cf in CustomField.objects.all():
        cf.org = org
        cf.save()
    for user in User.objects.all():
        user.current_organization = org
        user.save()
        GroupMember.objects.create(user=user, owner=direct)
        om = OrgMember.objects.create(user=user, owner=org)
        om.employee_number = user.employee_number
        om.hiredate = user.hiredate
        om.position = user.position
        om.remark = user.remark
        om.save()

    def g_child(grp):
        yield from Group.objects.filter(parent=grp)

    def g_successor(grp):
        for child in g_child(grp):
            yield from g_successor(child)

    for g_ in g_child(Group.objects.filter(uid='intra').first()):
        if g_.uid == 'role':
            for g in g_child(g_):
                g.parent = role
                g.save()
            for g in g_successor(g_):
                g.top = role.uid
                g.save()
        if g_.uid == 'label':
            for g in g_child(g_):
                g.parent = label
                g.save()
            for g in g_successor(g_):
                g.top = label.uid
                g.save()
        if g_.uid == 'manager':
            for g in g_child(g_):
                g.parent = manager
                g.save()
            for g in g_successor(g_):
                g.top = manager.uid
                g.save()
        else:
            g_.parent = group
            for g in g_successor(g_):
                g.top = g_.uid
                g.save()

    for d in Dept.objects.filter(parent=dept_root):
        d.parent = dept
        d.save()


def go(*args):
    if not settings.TESTING:
        migrate(*args)


class Migration(migrations.Migration):
    dependencies = [
        ('oneid_meta', '0069_auto_20200208_1834'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[('objects', models.manager.Manager())]
        ),
        migrations.RunPython(go),
    ]

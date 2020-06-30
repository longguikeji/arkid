'''
Migrate to multi-organization version
'''
# pylint: disable=invalid-name,too-many-locals,missing-class-docstring,missing-function-docstring

from uuid import uuid4
from django.db import migrations, models
from django.conf import settings


def migrate(apps, schema_editor):   # pylint: disable=unused-argument,too-many-branches,too-many-statements
    '''
    migrate with a default organization
    '''

    APP = apps.get_model('oneid_meta', 'APP')
    Log = apps.get_model('oneid_meta', 'Log')
    Org = apps.get_model('oneid_meta', 'Org')
    User = apps.get_model('oneid_meta', 'User')
    Dept = apps.get_model('oneid_meta', 'Dept')
    Perm = apps.get_model('oneid_meta', 'Perm')
    Group = apps.get_model('oneid_meta', 'Group')
    AppGroup = apps.get_model('oneid_meta', 'AppGroup')
    UserPerm = apps.get_model('oneid_meta', 'UserPerm')
    OrgMember = apps.get_model('oneid_meta', 'OrgMember')
    GroupMember = apps.get_model('oneid_meta', 'GroupMember')
    CustomField = apps.get_model('oneid_meta', 'CustomField')
    CompanyConfig = apps.get_model('oneid_meta', 'CompanyConfig')

    config = CompanyConfig.objects.all().first()
    name = config.fullname_cn
    if not name:
        name = '一账通'

    owner = None
    for user in User.objects.filter().all():
        if user.is_boss or user.username == 'admin'\
                or UserPerm.objects.filter(owner=user, perm__uid='system_oneid_all', value=True).exists():
            owner = user
            break

    dept_root = Dept.objects.filter(uid='root').first()
    group_root = Group.objects.filter(uid='root').first()
    app_group_root = AppGroup.objects.filter(uid='root').first()

    dept = Dept.objects.create(uid=str(uuid4()), name=f'{name}-部门', parent=dept_root)
    group = Group.objects.create(uid=str(uuid4()), name=f'{name}-分组', parent=group_root)
    app_group = AppGroup.objects.create(uid=str(uuid4()), name=f'{name}-应用分组', parent=app_group_root)
    direct = Group.objects.create(uid=str(uuid4()), name=f'{name}-直属成员', parent=group)
    manager = Group.objects.create(uid=str(uuid4()), name=f'{name}-管理员', parent=group)
    default_app_group = AppGroup.objects.create(uid=str(uuid4()), name=f'{name}-默认应用', parent=app_group)
    role = Group.objects.create(uid=str(uuid4()), name=f'{name}-角色', parent=group)
    label = Group.objects.create(uid=str(uuid4()), name=f'{name}-标签', parent=group)

    group.top = group.uid
    group.save()
    app_group.top = app_group.uid
    app_group.save()
    default_app_group.top = default_app_group.uid
    default_app_group.save()
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
        'app_group': app_group,
        'default_app_group': default_app_group,
        'role': role,
        'label': label,
    }
    org = Org.objects.create(**kw)

    oid = str(org.uuid)
    Perm.objects.create(name='创建大类', uid=f'{oid}_category_create', subject=oid, scope='category', action='create')
    Perm.objects.create(name='创建应用', uid=f'{oid}_app_create', subject=oid, scope='app', action='create')
    Perm.objects.create(name='查看日志', uid=f'{oid}_log_read', subject=oid, scope='log', action='read')
    Perm.objects.create(name='公司基本信息配置、基础设施配置', uid=f'{oid}_config_write', subject=oid, scope='config', action='write')
    Perm.objects.create(name='账号同步', uid=f'{oid}_account_sync', subject=oid, scope='account', action='sync')

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
    for user in User.objects.filter(is_del=False):
        user.current_organization = org
        user.save()
        GroupMember.objects.create(user=user, owner=direct)
        om = OrgMember.objects.create(user=user, owner=org)
        om.employee_number = user.employee_number
        om.hiredate = user.hiredate
        om.position = user.position
        om.remark = user.remark
        om.email = user.email
        om.save()

    # def g_child(grp):
    #     yield from Group.objects.filter(parent=grp)

    # def g_successor(grp, include_root=False):
    #     if include_root:
    #         yield grp
    #     for child in g_child(grp):
    #         yield from g_successor(child, include_root=True)

    for g in Group.objects.filter(parent__uid='intra'):
        g.parent = group
        g.save()
    intra = Group.objects.filter(uid='intra')
    if intra:
        intra.delete()

    for d in Dept.objects.filter(parent=dept_root).exclude(uid=dept.uid):
        d.parent = dept
        d.save()


def go(*args):
    if not settings.TESTING:
        migrate(*args)
    else:
        migrate(*args)


class Migration(migrations.Migration):
    dependencies = [
        ('oneid_meta', '0069_auto_20200208_1834'),
        ('oneid_meta', '0074_default_appgroup'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[('objects', models.manager.Manager())]
        ),
        migrations.RunPython(go),
    ]

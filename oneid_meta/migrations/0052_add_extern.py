
from django.db import migrations, models
from django.conf import settings

def create_extern(apps, schema_editor):
    '''
    创建默认外部联系人
    '''
    Group = apps.get_model('oneid_meta', 'Group')
    root, _ = Group.objects.get_or_create(uid='root')
    group, _ = Group.objects.get_or_create(uid='extern', parent=root)
    group.name = '外部联系人'
    group.save()

    return group

def rename_root_dept(apps, schema_editor):
    '''
    将 Dept(root).name 改为部门
    '''
    Dept = apps.get_model('oneid_meta', 'Dept')
    dept, _ = Dept.objects.get_or_create(uid='root')
    dept.name = '部门'
    dept.save()


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0051_rm_buildin_app'),
    ]

    operations = []
    if not settings.TESTING:
        operations += [
        migrations.RunPython(create_extern),
        migrations.RunPython(rename_root_dept),
    ]

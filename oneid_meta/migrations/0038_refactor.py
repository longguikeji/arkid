

from django.db import migrations, models
from django.conf import settings


def move_manager_group_under_intra(apps, schema_editor):
    Group = apps.get_model('oneid_meta', 'Group')
    intra, _ = Group.objects.get_or_create(uid='intra')
    manager_group = Group.objects.filter(uid='manager').first()
    if not manager_group:
        manager_group = Group.objects.create(uid='manager')

    manager_group.parent = intra
    manager_group.name = '子管理员组'
    manager_group.top = 'manager'
    manager_group.save()


def create_native_group(apps, schema_editor):
    Group = apps.get_model('oneid_meta', 'Group')
    intra, _ = Group.objects.get_or_create(uid='intra')

    role, _ = Group.objects.get_or_create(uid='role')
    role.parent = intra
    role.name = '角色'
    role.top = role.uid
    role.save()

    label, _ = Group.objects.get_or_create(uid='label')
    label.parent = intra
    label.name = '标签'
    label.top = label.uid
    label.save()

class Migration(migrations.Migration):


    dependencies = [
        ('oneid_meta', '0037_group_top'),
    ]

    operations = []

    if not settings.TESTING:
        operations += [
            migrations.RunPython(move_manager_group_under_intra)
        ]

    if not settings.TESTING and settings.SITE_META.lower() == 'native':
        operations += [
            migrations.RunPython(create_native_group),
        ]

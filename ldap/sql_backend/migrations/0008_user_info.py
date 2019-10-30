
from django.db import migrations, models


def add_user_attrs(apps, schema_editor):
    '''
    添加用户字段
    '''
    LDAPOCMappings = apps.get_model('sql_backend', 'LDAPOCMappings')
    LDAPAttrMapping = apps.get_model('sql_backend', 'LDAPAttrMapping')
    inetOrgPerson = LDAPOCMappings.objects.get(name='inetOrgPerson')
    table_name = 'oneid_meta_user'
    for (name, sel_expr, join_where, create_proc, delete_proc, param_order, expect_return) in [
        # ('uid', 'oneid_meta_user.username', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        # ('cn', 'oneid_meta_user.username', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        # ('userPassword', 'oneid_meta_user.password', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        ('mail', 'oneid_meta_user.email', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        ('name', 'oneid_meta_user.name', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        ('telephoneNumber', 'oneid_meta_user.mobile', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
    ]:
        LDAPAttrMapping.objects.create(
            oc_map=inetOrgPerson,
            name=name,
            sel_expr=sel_expr,
            from_tbls=table_name,
            join_where=join_where,
            create_proc=create_proc,
            delete_proc=delete_proc,
            param_order=param_order,
            expect_return=expect_return,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('sql_backend', '0007_update_group_member'),
    ]

    operations = [
        migrations.RunPython(add_user_attrs),
    ]

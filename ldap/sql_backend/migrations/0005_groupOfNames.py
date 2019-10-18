
from django.db import migrations, models
from ldap.sql_backend.models import (
    LDAPOCMappings,
    LDAPAttrMapping,
)


def create_ldap_oc_mappings(app, schema_editor):

    LDAPOCMappings.objects.create(
        name='groupOfNames',
        keytbl='ldap_group',
        keycol='id',
        create_proc=None,
        delete_proc=None,
        expect_return=0,
    )


def creata_ldap_attr_mappings(app, schema_editor):

    groupOfNames = LDAPOCMappings.objects.get(name='groupOfNames')
    for (name, sel_expr, from_tables, join_where, create_proc, delete_proc, param_order, expect_return) in [
        ('cn', 'ldap_group.uid', 'ldap_group', None, None, None, 3, 0),
        (#  deprecated
            'member',
            'distinct ldap_entries.dn',
            'oneid_meta_groupmember ogm, ldap_group, oneid_meta_deptmember odm, ldap_entries',
            '( \
                (ogm.owner_id =ldap_group.id - 100000 and ogm.user_id=ldap_entries.keyval) \
                or \
                (odm.owner_id =ldap_group.id and odm.user_id=ldap_entries.keyval) \
            ) and ldap_entries.oc_map_id = 4',
            None, None, 3, 0,
        )
    ]:
        LDAPAttrMapping.objects.create(
            oc_map=groupOfNames,
            name=name,
            sel_expr=sel_expr,
            from_tbls=from_tables,
            join_where=join_where,
            create_proc=create_proc,
            delete_proc=delete_proc,
            param_order=param_order,
            expect_return=expect_return,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('sql_backend', '0004_create_group_view'),
    ]

    operations = [
        migrations.RunPython(create_ldap_oc_mappings),
        migrations.RunPython(creata_ldap_attr_mappings),
    ]

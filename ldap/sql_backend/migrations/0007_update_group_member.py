from django.db import migrations


def update_ldap_attr_mappings_member(apps, schema_editor):
    '''
    update groupOfNames.member
    '''
    LDAPOCMappings = apps.get_model('sql_backend', 'LDAPOCMappings')
    LDAPAttrMapping = apps.get_model('sql_backend', 'LDAPAttrMapping')
    groupOfNames = LDAPOCMappings.objects.get(name='groupOfNames')

    member = LDAPAttrMapping.objects.filter(name='member', oc_map=groupOfNames).first()
    if member:
        member.delete()

    for (name, sel_expr, from_tables, join_where, create_proc, delete_proc, param_order, expect_return) in [
        (
            'member',
            'member_entries.dn',
            'ldap_group, ldap_group_member, ldap_entries AS member_entries',
            'ldap_group_member.user_id=member_entries.keyval and ldap_group_member.owner_id =ldap_group.id and member_entries.oc_map_id = 4' ,
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
        ('sql_backend', '0006_create_task'),
    ]

    # group id += 10w,以和dept区分
    ldap_group_view = '''
CREATE VIEW ldap_group (id, uid, name, parent_id, subject) AS
        (SELECT id, uid, name, parent_id, 2 FROM oneid_meta_dept WHERE oneid_meta_dept.is_del=false)
    UNION
        (SELECT id + 100000, uid, name, parent_id, 3 FROM oneid_meta_group WHERE oneid_meta_group.is_del=false)
;
'''

    ldap_group_member_view = '''
    CREATE VIEW ldap_group_member (id, owner_id, user_id, subject) AS
        (SELECT id, owner_id, user_id, 2 FROM oneid_meta_deptmember)
    UNION
        (SELECT id, owner_id + 100000, user_id, 3 FROM oneid_meta_groupmember)
    '''

    operations = [
        migrations.RunSQL('drop view if exists ldap_group;'),
        migrations.RunSQL(ldap_group_view),
        migrations.RunSQL('drop view if exists ldap_group_member;'),
        migrations.RunSQL(ldap_group_member_view),
        migrations.RunPython(update_ldap_attr_mappings_member),
    ]

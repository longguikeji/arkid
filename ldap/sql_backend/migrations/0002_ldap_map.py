
from django.db import migrations, models
from ldap.sql_backend.models import (
    LDAPOCMappings,
    LDAPAttrMapping,
    LDAPEntry,
    LDAPEntryObjectclasses,
    Organization,
    OrganizationUnit,
    DomainComponent,
)


def create_objects(apps, schema_editor):

    DomainComponent.objects.create(
        name='example',
        dc='example',
    )

    Organization.objects.create(
        name='example',
        o='Example Inc.',
    )

    OrganizationUnit.objects.create(
        name='用户',
        ou='people',
    )

    OrganizationUnit.objects.create(
        name='部门',
        ou='dept',
    )

    OrganizationUnit.objects.create(
        name='组',
        ou='group',
    )


def create_ldap_oc_mappings(apps, schema_editor):

    LDAPOCMappings.objects.create(
        name='dcObject',
        keytbl='domain_component',
        keycol='id',
        create_proc=None,
        delete_proc=None,
        expect_return=0,
    )
    LDAPOCMappings.objects.create(
        name='organization',
        keytbl='organization',
        keycol='id',
        create_proc=None,
        delete_proc=None,
        expect_return=0,
    )
    LDAPOCMappings.objects.create(
        name='organizationalUnit',
        keytbl='organization_unit',
        keycol='id',
        create_proc=None,
        delete_proc=None,
        expect_return=0,
    )
    LDAPOCMappings.objects.create(
        name='inetOrgPerson',
        keytbl='oneid_meta_user',
        keycol='id',
        create_proc=None,
        delete_proc=None,
        expect_return=0,
    )


def creata_ldap_attr_mappings(apps, schema_editor):

    dcObject = LDAPOCMappings.objects.get(name='dcObject')
    table_name = 'domain_component'
    for (name, sel_expr, join_where, create_proc, delete_proc, param_order, expect_return) in [
        ('dc', 'domain_component.dc', None, None, None, 3, 0),
    ]:
        LDAPAttrMapping.objects.create(
            oc_map=dcObject,
            name=name,
            sel_expr=sel_expr,
            from_tbls=table_name,
            join_where=join_where,
            create_proc=create_proc,
            delete_proc=delete_proc,
            param_order=param_order,
            expect_return=expect_return,
        )

    organization = LDAPOCMappings.objects.get(name='organization')
    table_name = 'organization'
    for (name, sel_expr, join_where, create_proc, delete_proc, param_order, expect_return) in [
        ('o', 'organization.o', None, None, None, 3, 0),
    ]:
        LDAPAttrMapping.objects.create(
            oc_map=organization,
            name=name,
            sel_expr=sel_expr,
            from_tbls=table_name,
            join_where=join_where,
            create_proc=create_proc,
            delete_proc=delete_proc,
            param_order=param_order,
            expect_return=expect_return,
        )

    organizationalUnit = LDAPOCMappings.objects.get(name='organizationalUnit')
    table_name = 'organization_unit'
    for (name, sel_expr, join_where, create_proc, delete_proc, param_order, expect_return) in [
        ('ou', 'organization_unit.ou', None, None, None, 3, 0)
    ]:
        LDAPAttrMapping.objects.create(
            oc_map=organizationalUnit,
            name=name,
            sel_expr=sel_expr,
            from_tbls=table_name,
            join_where=join_where,
            create_proc=create_proc,
            delete_proc=delete_proc,
            param_order=param_order,
            expect_return=expect_return,
        )

    inetOrgPerson = LDAPOCMappings.objects.get(name='inetOrgPerson')
    table_name = 'oneid_meta_user'
    for (name, sel_expr, join_where, create_proc, delete_proc, param_order, expect_return) in [
        ('uid', 'oneid_meta_user.username', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        ('cn', 'oneid_meta_user.username', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
        ('userPassword', 'oneid_meta_user.password', 'oneid_meta_user.is_del=FALSE', None, None, 3, 0),
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


def create_entry(app, schema_editor):
    dc_class = LDAPOCMappings.objects.get(name='dcObject')
    domain_component = DomainComponent.objects.get(dc='example')
    base_entry = LDAPEntry.objects.create(
        dn='dc=example,dc=org',
        oc_map=dc_class,
        parent=None,
        keyval=domain_component.id,
    )
    LDAPEntryObjectclasses.objects.create(
        entry=base_entry,
        oc_name='organization'
    )

    ou_class = LDAPOCMappings.objects.get(name='organizationalUnit')
    people_ou = OrganizationUnit.objects.get(ou='people')
    people_ou_entry = LDAPEntry.objects.create(
        dn='ou={},dc=example,dc=org'.format(people_ou.ou),
        oc_map=ou_class,
        parent=base_entry,
        keyval=people_ou.id,)

    dept_ou = OrganizationUnit.objects.get(ou='dept')
    dept_ou_entry = LDAPEntry.objects.create(
        dn='ou={},dc=example,dc=org'.format(dept_ou.ou),
        oc_map=ou_class,
        parent=base_entry,
        keyval=dept_ou.id,)

    group_ou = OrganizationUnit.objects.get(ou='group')
    group_ou_entry = LDAPEntry.objects.create(
        dn='ou={},dc=example,dc=org'.format(group_ou.ou),
        oc_map=ou_class,
        parent=base_entry,
        keyval=group_ou.id,)


class Migration(migrations.Migration):

    dependencies = [
        ('sql_backend', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_objects),
        migrations.RunPython(create_ldap_oc_mappings),
        migrations.RunPython(creata_ldap_attr_mappings),
        migrations.RunPython(create_entry),
    ]

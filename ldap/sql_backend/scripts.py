'''
确保db中的dn正确，供LDAP查询
'''

from celery import shared_task

from oneid_meta.models import User, Group, Dept, GroupMember, DeptMember
from ldap.sql_backend.models import LDAPEntry as Entry
from ldap.sql_backend.models import LDAPOCMappings as OCMap


def flush_user_entries():
    '''
    维护user LDAP Entries
    '''
    entry_subject = 1
    oc_map = OCMap.objects.get(name='inetOrgPerson')
    user_base = Entry.objects.get(dn='ou=people,dc=example,dc=org')
    for user in User.valid_objects.all():
        dn = 'uid={},ou=people,dc=example,dc=org'.format(user.username)
        entry = Entry.objects.filter(dn=dn).first()
        if entry:
            if entry.oc_map != oc_map:
                entry.oc_map = oc_map
            if entry.parent != user_base:
                entry.parent = user_base
            if entry.keyval != user.id:
                entry.keyval = user.id
            if entry.subject != entry_subject:
                entry.subject = entry_subject
            entry.save()
        else:
            Entry.objects.create(
                dn=dn,
                oc_map=oc_map,
                parent=user_base,
                keyval=user.id,
                subject=entry_subject,
            )


def flush_group():
    '''
    维护 group LDAP Entries
    '''
    entry_subject = 3
    oc_map = OCMap.objects.get(name='groupOfNames')
    group_base = Entry.objects.get(dn='ou=group,dc=example,dc=org')
    for group in Group.valid_objects.exclude(uid='root'):
        dn = ','.join([f"cn={uid.replace('g_', '')}"
                       for uid in list(group.upstream_uids)][:-1]) + ',ou=group,dc=example,dc=org'
        entry = Entry.objects.filter(dn=dn).first()
        if entry:
            if entry.oc_map != oc_map:
                entry.oc_map = oc_map
            if entry.parent != group_base:
                entry.parent = group_base
            if entry.keyval != group.id:
                entry.keyval = group.id
            if entry.subject != entry_subject:
                entry.subject = entry_subject
            entry.save()
        else:
            Entry.objects.create(
                dn=dn,
                oc_map=oc_map,
                parent=group_base,
                keyval=group.id,
                subject=entry_subject,
            )


def flush_dept_entries():
    '''
    维护 dept LDAP Entries
    '''
    entry_subject = 2
    oc_map = OCMap.objects.get(name='groupOfNames')
    dept_base = Entry.objects.get(dn='ou=dept,dc=example,dc=org')
    for dept in Dept.valid_objects.exclude(uid='root'):
        dn = ','.join([f"cn={uid.replace('d_', '')}"
                       for uid in list(dept.upstream_uids)][:-1]) + ',ou=dept,dc=example,dc=org'
        entry = Entry.objects.filter(dn=dn).first()
        if entry:
            if entry.oc_map != oc_map:
                entry.oc_map = oc_map
            if entry.parent != dept_base:
                entry.parent = dept_base
            if entry.keyval != dept.id:
                entry.keyval = dept.id
            if entry.subject != entry_subject:
                entry.subject = entry_subject
            entry.save()
        else:
            Entry.objects.create(
                dn=dn,
                oc_map=oc_map,
                parent=dept_base,
                keyval=dept.id,
                subject=entry_subject,
            )


def insert_test_data():
    root = Group.objects.get(uid='root')
    Group.objects.get_or_create(parent=root, uid='level', name='level')
    user = User.objects.get(username='admin')
    GroupMember.objects.get_or_create(user=user, owner=root)

    root = Dept.objects.get(uid='root')
    Dept.objects.get_or_create(parent=root, uid='level', name='level')
    user = User.objects.get(username='admin')
    DeptMember.objects.get_or_create(user=user, owner=root)

    user = User.objects.create(username='test')
    root = Dept.objects.get(uid='root')
    DeptMember.objects.create(user=user, owner=root)


@shared_task
def flush_entries():
    '''
    维护LDAP Entries
    '''
    # insert_test_data()
    flush_group()
    flush_user_entries()
    flush_dept_entries()

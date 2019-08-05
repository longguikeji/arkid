
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sql_backend', '0002_ldap_map'),
    ]

# group id += 10w,以和dept区分

    sql = '''
CREATE VIEW ldap_entries (id, dn, oc_map_id, parent, keyval, subject) AS
    (SELECT id, dn, oc_map_id, parent_id, keyval, subject \
        FROM raw_ldap_entries WHERE raw_ldap_entries.subject != 3)
UNION
    (SELECT id, dn, oc_map_id, parent_id, keyval + 100000, subject \
        FROM raw_ldap_entries WHERE raw_ldap_entries.subject = 3)
'''

    operations = [
        migrations.RunSQL('drop view if exists ldap_entries;'),
        migrations.RunSQL(sql),
    ]

'''
deprecated
'''
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('sql_backend', '0003_create_ldap_entries_view'),
    ]

# group id += 10w,以和dept区分

    sql = '''
CREATE VIEW ldap_group (id, uid, name, parent_id, subject) AS
        (SELECT id, uid, name, parent_id, 2 FROM oneid_meta_dept)
    UNION
        (SELECT id + 100000, uid, name, parent_id, 3 FROM oneid_meta_group)
;
'''

    operations = [
        migrations.RunSQL('drop view if exists ldap_group;'),
        migrations.RunSQL(sql),
    ]

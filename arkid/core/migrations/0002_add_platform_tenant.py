from django.db import migrations

class Migration(migrations.Migration):

    def add_platform_tenant(apps, schema_editor):
        from arkid.core.models import Tenant
        Tenant.objects.get_or_create(
            slug='',  
            name="platform tenant",
        )

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_platform_tenant),
    ]
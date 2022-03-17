# Generated by Django 3.1.7 on 2021-03-28 14:03

from django.db import migrations


def remove_config(apps, schema_editor):
    from extension_root.tenantuserconfig.models import TenantUserConfig
    TenantUserConfig.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tenantuserconfig', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_config),
    ]
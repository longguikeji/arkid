# Generated by Django 4.0.6 on 2022-10-26 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_alter_tenant_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='expiringtoken',
            name='active_date',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='Active Date'),
        ),
    ]

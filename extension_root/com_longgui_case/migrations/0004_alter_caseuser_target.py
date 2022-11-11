# Generated by Django 4.0.7 on 2022-11-08 07:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_expiringtoken_active_date'),
        ('com_longgui_case', '0003_alter_caseuser_nickname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseuser',
            name='target',
            field=models.OneToOneField(blank=True, default=None, on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s', to='core.user'),
        ),
    ]
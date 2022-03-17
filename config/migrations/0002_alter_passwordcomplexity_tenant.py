# Generated by Django 3.2.6 on 2021-09-03 06:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant', '0024_auto_20210903_0422'),
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordcomplexity',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='tenant.tenant', verbose_name='租户'),
        ),
    ]
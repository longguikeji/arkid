# Generated by Django 3.2.13 on 2022-06-15 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_merge_0013_merge_20220602_0918_0013_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='url',
            field=models.CharField(blank=True, max_length=1024, null=True, verbose_name='url'),
        ),
    ]

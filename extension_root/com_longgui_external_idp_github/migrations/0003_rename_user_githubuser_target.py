# Generated by Django 3.2.13 on 2022-05-31 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('com_longgui_external_idp_github', '0002_auto_20220531_1427'),
    ]

    operations = [
        migrations.RenameField(
            model_name='githubuser',
            old_name='user',
            new_name='target',
        ),
    ]

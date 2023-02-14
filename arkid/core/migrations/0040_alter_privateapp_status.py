# Generated by Django 4.0.6 on 2023-02-14 03:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_app_skip_token_verification'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privateapp',
            name='status',
            field=models.CharField(choices=[('install_success', 'Install Success'), ('installing', 'Installing'), ('install_fail', 'Install Fail'), ('deleted', 'Deleted')], default='installing', max_length=100, verbose_name='Status'),
        ),
    ]

# Generated by Django 3.2.6 on 2021-08-11 01:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('provisioning', '0004_auto_20210702_0223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='auth_type',
            field=models.IntegerField(choices=[('basic', 'Basic Auth'), ('token', 'Token Auth')], default='token', max_length=32),
        ),
        migrations.AlterField(
            model_name='config',
            name='status',
            field=models.IntegerField(choices=[('enabled', 'Enabled'), ('disabled', 'Disabled')], default='disabled'),
        ),
        migrations.AlterField(
            model_name='config',
            name='sync_type',
            field=models.IntegerField(choices=[('upstream', 'Upstream'), ('downstream', 'Downstream')], default='downstream', max_length=32),
        ),
    ]

# Generated by Django 3.2.13 on 2022-06-20 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extension', '0006_alter_extension_labels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extension',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='是否启动'),
        ),
    ]

# Generated by Django 4.0.6 on 2022-12-15 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extension', '0012_alter_extension_author_alter_extension_homepage_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='expired',
            field=models.BooleanField(default=False, verbose_name='expired'),
        ),
    ]
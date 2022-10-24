# Generated by Django 4.0.6 on 2022-10-20 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extension', '0011_extension_author_extension_homepage_extension_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extension',
            name='author',
            field=models.CharField(blank=True, default='', max_length=128, null=True, verbose_name='Author'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='homepage',
            field=models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='Homepage'),
        ),
        migrations.AlterField(
            model_name='extension',
            name='logo',
            field=models.CharField(blank=True, default='', max_length=1024, null=True, verbose_name='Logo'),
        ),
    ]
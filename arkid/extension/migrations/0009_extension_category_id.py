# Generated by Django 3.2.13 on 2022-09-13 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extension', '0008_tenantextension_is_rented'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='category_id',
            field=models.IntegerField(default=None, null=True, verbose_name='ArkStore分类ID'),
        ),
    ]

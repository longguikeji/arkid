# Generated by Django 3.2.8 on 2022-02-22 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0029_merge_20210922_0729'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=128),
        ),
    ]

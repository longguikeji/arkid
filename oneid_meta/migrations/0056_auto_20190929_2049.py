# Generated by Django 2.0.13 on 2019-09-29 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0055_user_last_active_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='dinguser',
            name='ding_id',
            field=models.TextField(blank=True, max_length=255, verbose_name='钉钉ID'),
        ),
        migrations.AddField(
            model_name='dinguser',
            name='open_id',
            field=models.TextField(blank=True, max_length=255, verbose_name='用户在当前开放应用内的唯一标识'),
        ),
        migrations.AddField(
            model_name='dinguser',
            name='union_id',
            field=models.TextField(blank=True, max_length=255, verbose_name='用户在当前开放应用所属的钉钉开放平台账号内的唯一标识'),
        ),
    ]
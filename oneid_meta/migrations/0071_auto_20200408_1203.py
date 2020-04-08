# Generated by Django 2.2.10 on 2020-04-08 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oneid_meta', '0070_auto_20200402_1602'),
    ]

    operations = [
        migrations.AddField(
            model_name='dingconfig',
            name='sync_state',
            field=models.CharField(choices=[('pull', '拉取'), ('push', '推送'), ('', '断开')], default='pull', max_length=128, verbose_name='同步钉钉账户方向'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_alipay_qr',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否开放支付宝扫码登录'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_ding_qr',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否开放钉钉扫码登录'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_email',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否允许邮箱(注册、)登录、找回密码'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_mobile',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否允许手机(注册、)登录、找回密码'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_qq_qr',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否开放qq扫码登录'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_register',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否开放注册'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_wechat_qr',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否开放微信扫码登录'),
        ),
        migrations.AlterField(
            model_name='accountconfig',
            name='allow_work_wechat_qr',
            field=models.BooleanField(blank=True, default=False, verbose_name='是否开放企业微信扫码登录'),
        ),
        migrations.AlterField(
            model_name='emailconfig',
            name='is_valid',
            field=models.BooleanField(blank=True, default=False, verbose_name='配置是否有效'),
        ),
        migrations.AlterField(
            model_name='group',
            name='accept_user',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AlterField(
            model_name='minioconfig',
            name='secure',
            field=models.BooleanField(blank=True, default=True, max_length=225, verbose_name='SECURE'),
        ),
        migrations.AlterField(
            model_name='smsconfig',
            name='is_valid',
            field=models.BooleanField(blank=True, default=False, verbose_name='配置是否有效'),
        ),
    ]

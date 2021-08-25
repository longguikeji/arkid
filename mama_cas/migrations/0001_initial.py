# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyGrantingTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket', models.CharField(unique=True, max_length=255, verbose_name='ticket')),
                ('expires', models.DateTimeField(verbose_name='expires')),
                ('consumed', models.DateTimeField(null=True, verbose_name='consumed')),
                ('iou', models.CharField(unique=True, max_length=255, verbose_name='iou')),
            ],
            options={
                'verbose_name': 'proxy-granting ticket',
                'verbose_name_plural': 'proxy-granting tickets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProxyTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket', models.CharField(unique=True, max_length=255, verbose_name='ticket')),
                ('expires', models.DateTimeField(verbose_name='expires')),
                ('consumed', models.DateTimeField(null=True, verbose_name='consumed')),
                ('service', models.CharField(max_length=255, verbose_name='service')),
                ('granted_by_pgt', models.ForeignKey(verbose_name='granted by proxy-granting ticket', to='mama_cas.ProxyGrantingTicket', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'proxy ticket',
                'verbose_name_plural': 'proxy tickets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceTicket',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticket', models.CharField(unique=True, max_length=255, verbose_name='ticket')),
                ('expires', models.DateTimeField(verbose_name='expires')),
                ('consumed', models.DateTimeField(null=True, verbose_name='consumed')),
                ('service', models.CharField(max_length=255, verbose_name='service')),
                ('primary', models.BooleanField(default=False, verbose_name='primary')),
                ('user', models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'service ticket',
                'verbose_name_plural': 'service tickets',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='granted_by_pt',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='granted by proxy ticket', blank=True, to='mama_cas.ProxyTicket', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='granted_by_st',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='granted by service ticket', blank=True, to='mama_cas.ServiceTicket', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='proxygrantingticket',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]

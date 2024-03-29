# Generated by Django 3.2.13 on 2022-05-20 04:54

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('name', models.CharField(max_length=128)),
                ('url', models.CharField(max_length=1024)),
                ('secret', models.CharField(blank=True, max_length=128, null=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebhookTriggerHistory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('status', models.CharField(choices=[('waiting', 'Waiting'), ('success', 'Success'), ('failed', 'Failed')], default='waiting', max_length=128)),
                ('request', models.TextField(blank=True, null=True, verbose_name='Http Request')),
                ('response', models.TextField(blank=True, null=True, verbose_name='Http Response')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.tenant')),
                ('webhook', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='history_set', related_query_name='histories', to='webhook.webhook')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WebhookEvent',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, unique=True, verbose_name='ID')),
                ('is_del', models.BooleanField(default=False, verbose_name='是否删除')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否可用')),
                ('updated', models.DateTimeField(auto_now=True, null=True, verbose_name='更新时间')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='创建时间')),
                ('event_type', models.CharField(db_index=True, max_length=128, verbose_name='Event type')),
                ('webhooks', models.ManyToManyField(blank=True, related_name='events_set', related_query_name='events', to='webhook.Webhook')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# Generated by Django 3.2.8 on 2022-01-12 16:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oauth2_provider', '0007_application_custom_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesstoken',
            name='tenant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.tenant'),
        ),
        migrations.AddField(
            model_name='idtoken',
            name='tenant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.tenant'),
        ),
    ]

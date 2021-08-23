from django.db import migrations


class Migration(migrations.Migration):

    def add_default_data(self, schema_editor):
        from oneid_meta.models.app import OAuthAPP
        apps = OAuthAPP.objects.all()
        for app in apps:
            app.skip_authorization = True
            app.save()
    dependencies = [
        ('oneid_meta', '0083_init_contactsconfig'),
    ]

    operations = [
        migrations.RunPython(add_default_data),
    ]

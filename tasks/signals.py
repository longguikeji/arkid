from django.db.models.signals import post_save
from tenant.models import Tenant
from inventory.models import User, Group, Permission
from app.models import App
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _


def tenant_saved(sender, instance: Tenant, created: bool, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(Tenant)
        Permission.objects.get_or_create(
            tenant=instance,
            content_type=content_type,            
            codename=f'tenant_admin_{instance.uuid}',            
            name=_('Can admin tenant') + f' {instance.name}',
        )


def user_saved(sender, instance: User, created: bool, **kwargs):
    print('signal user saved', sender, instance, created, kwargs)
    from tasks.tasks import provision_user
    # provision_user(instance.tenant.id, instance.id)


def group_saved(sender, instance: Group, created: bool, **kwargs):
    print('signal group saved', sender, instance, created, kwargs)


def app_saved(sender, instance: App, created: bool, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(App)
        Permission.objects.create(
            tenant=instance.tenant,
            codename=f'app_access_{instance.uuid}',
            name=_('Can access app') + f' {instance.name}',
            content_type=content_type,
        )
    else:
        if instance.is_del:
            Permission.objects.filter(
                tenant=instance.tenant,
                codename=f'app_access_{instance.uuid}',
            ).delete()


post_save.connect(receiver=tenant_saved, sender=Tenant)

post_save.connect(receiver=app_saved, sender=App)

post_save.connect(receiver=user_saved, sender=User)
post_save.connect(receiver=group_saved, sender=Group)
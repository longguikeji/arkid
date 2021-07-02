from django.db.models.signals import post_save, pre_delete, m2m_changed
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

    tenants = instance.tenants.all()
    if not tenants:
        print('User with no tenants!')
        return

    for tenant in instance.tenants.all():
        # provision_user.delay(tenant.uuid, instance.id)
        provision_user(tenant.uuid, instance.id)

def user_deleted(sender, instance: User, **kwargs):
    print('signal user deleted', sender, kwargs)
    from tasks.tasks import provision_user

    tenants = instance.tenants.all()
    if not tenants:
        print('User with no tenants!')
        return

    for tenant in instance.tenants.all():
        # provision_user.delay(tenant.uuid, instance.id)
        provision_user(tenant.uuid, instance.id, is_del=True)

def group_saved(sender, instance: Group, created: bool, **kwargs):
    print('signal group saved', sender, instance, created, kwargs)
    from tasks.tasks import provision_group

    tenant = instance.tenant
    if not tenant:
        print('Group with no tenant!')
        return

    # provision_group.delay(tenant.uuid, instance.id)
    provision_group(tenant.uuid, instance.id)

def group_deleted(sender, instance: User, **kwargs):
    print('signal group deleted', sender, kwargs)
    from tasks.tasks import provision_group

    tenant = instance.tenant
    if not tenant:
        print('Group with no tenants!')
        return

        # provision_user.delay(tenant.uuid, instance.id)
    provision_group(tenant.uuid, instance.id, is_del=True)


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

def user_groups_changed(sender, **kwargs):
    from tasks.tasks import provision_user_groups_changed
    action = kwargs.get('action')
    instance = kwargs.get('instance')
    pk_set = kwargs.get('pk_set')
    reverse = kwargs.get('reverse')
    if reverse:
        # Arkid暂时只有改变User的Group, 改变Group包含的User暂不支持
        return
    if action not in ('pre_clear', 'pre_add', 'pre_remove'):
        return
    for tenant in instance.tenants.all():
        provision_user_groups_changed(tenant.uuid, action, instance.id, pk_set)

post_save.connect(receiver=tenant_saved, sender=Tenant)

post_save.connect(receiver=app_saved, sender=App)

post_save.connect(receiver=user_saved, sender=User)
post_save.connect(receiver=group_saved, sender=Group)

# 如果用post_delete, 取不到用户的租户信息
pre_delete.connect(receiver=user_deleted, sender=User)
pre_delete.connect(receiver=group_deleted, sender=Group)

m2m_changed.connect(receiver=user_groups_changed, sender=User.groups.through)

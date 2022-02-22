from .models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.db.utils import IntegrityError


@receiver(m2m_changed, sender=User.tenants.through)
def verify_user_tenant_uniqueness(sender, **kwargs):
    """
    manytomany filed unique together: User and Tenant
    """
    user = kwargs.get('instance', None)
    action = kwargs.get('action', None)
    tenants = kwargs.get('pk_set', None)

    if action == 'pre_add':
        for tenant in tenants:
            if User.objects.filter(username=user.username).filter(tenants=tenant):
                raise IntegrityError('User with username %s already exists for tenant %s' % (user.username, tenant))

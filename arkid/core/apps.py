from django.apps import AppConfig

class CoreConfig(AppConfig):

    name = 'arkid.core'

    def ready(self):
        try:
            from arkid.core.models import Tenant, User
            tenant, _ = Tenant.objects.get_or_create(
                slug='',
                name="platform tenant",
            )
            user, created = User.objects.get_or_create(
                username="admin",
            )
            user.tenants.add(tenant)
            user.save()
        except:
            pass

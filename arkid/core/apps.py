from django.apps import AppConfig

class CoreConfig(AppConfig):

    name = 'arkid.core'

    def ready(self):
        try:
            from arkid.core.models import Tenant, User
            tenant, _ = Tenant.objects.get_or_create(
                # slug='',
                name="platform tenant",
            )
            user, _ = User.objects.get_or_create(
                username="admin",
                tenant=tenant,
            )
            tenant.create_tenant_user_admin_permission(user)
            tenant.users.add(user)
            tenant.save()

        except:
            pass
        # 监听
        from arkid.core import listener

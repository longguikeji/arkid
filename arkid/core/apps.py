import os
from django.apps import AppConfig


class CoreConfig(AppConfig):

    name = 'arkid.core'

    def ready(self):
        run_once = os.environ.get('CMDLINERUNNER_RUN_ONCE')
        if run_once is not None:
            return
        os.environ['CMDLINERUNNER_RUN_ONCE'] = 'True'
        try:
            from arkid.core.models import Tenant, User
            tenant = Tenant.objects.filter(
                slug=''
            ).first()
            if tenant is None:
                tenant = Tenant()
                tenant.slug = ''
                tenant.name = '平台租户'
                tenant.save()
            user, _ = User.objects.get_or_create(
                username="admin",
                tenant=tenant,
            )
            tenant.create_tenant_user_admin_permission(user)
            tenant.users.add(user)
            tenant.save()
        except Exception as e:
            print(e)

        # 监听
        from arkid.core import listener

        try:
            from arkid import settings
            from arkid.core.models import Platform
            config = Platform.get_config()
            if config.frontend_url:
                settings.CSRF_TRUSTED_ORIGINS.append(config.frontend_url)
        except Exception as e:
            print(e)

from django.urls import reverse
from requestlogs.entries import RequestLogEntry
from tenant.models import Tenant
from inventory.models import User


class CustomRequestLogEntry(RequestLogEntry):
    @property
    def host(self):
        host = self.django_request.get_host().split(':')[0]
        return host

    @property
    def user(self):
        ret = {
            'uuid': None,
            'username': None,
            'admin': False,
        }

        log_user = None

        # get user after user token authentication
        user = self._user or getattr(self.django_request, 'user', None)
        if user and user.is_authenticated:
            log_user = user

        # get user from login
        if not log_user and self.request.path == reverse('api:login'):
            try:
                username = self.django_request.cached_request_data.get('username')
                user = User.objects.filter(username=username).first()
                if user:
                    log_user = user
                else:
                    ret['username'] = username
            except Exception as e:
                pass

        if log_user:
            ret['uuid'] = str(log_user.uuid)
            ret['username'] = log_user.username
            ret['admin'] = log_user.is_staff

        return ret

    @property
    def tenant(self):
        ret = {
            'uuid': None,
            'name': None,
            'slug': None,
        }
        tenant = None

        # get tenant from context
        try:
            context = self.view_obj.get_serializer_context()
            tenant = context['tenant']
        except:
            pass

        # get tenant from slug
        if not tenant:
            try:
                slug = self.host.split('.')[0]
                tenant = Tenant.objects.filter(slug=slug).first()
            except:
                pass

        # get tenant from request params
        if not tenant:
            try:
                tenant_uuid = self.drf_request.parser_context.get('kwargs').get('tenant')
                tenant = Tenant.objects.filter(uuid=tenant_uuid).first()
            except:
                pass

        # use default tenant
        if not tenant:
            tenant = Tenant.objects.all().order_by('id').first()

        if tenant:
            ret['uuid'] = str(tenant.uuid)
            ret['name'] = tenant.name
            ret['slug'] = tenant.slug

        return ret

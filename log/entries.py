from requestlogs.entries import RequestLogEntry
from tenant.models import Tenant


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
            'admin': None,
        }

        user = self._user or getattr(self.django_request, 'user', None)
        if user and user.is_authenticated:
            ret['uuid'] = str(user.uuid)
            ret['username'] = user.username
            ret['admin'] = user.is_staff

        return ret

    @property
    def tenant(self):
        ret = {
            'uuid': None,
            'name': None,
            'slug': None,
        }
        tenant = None

        try:
            context = self.view_obj.get_serializer_context()
            tenant = context['tenant']
        except:
            pass

        if not tenant:
            try:
                slug = self.host.split('.')[0]
                tenant = Tenant.objects.filter(slug=slug).first()
            except:
                pass

        if tenant:
            ret['uuid'] = str(tenant.uuid)
            ret['name'] = tenant.name
            ret['slug'] = tenant.slug

        return ret

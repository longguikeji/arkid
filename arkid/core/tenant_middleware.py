import re
import json
from django.urls import resolve
from arkid.core.models import Tenant
from arkid.config import get_app_config


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        tenant = None
        tenant_not_found = False
    
        path = request.path
        uuid4hex = re.compile('tenant[s]?/[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}', re.I)
        matchs = uuid4hex.findall(path)
        for match in matchs:
            if match.startswith('tenants'):
                match = match[8:]
            else:
                match = match[7:]
            tenant = Tenant.active_objects.filter(id=match).first()
            if tenant:
                break
        if not tenant and matchs:
            tenant_not_found = True
        
        tenant_id = request.GET.get("tenant_id")
        if not tenant and tenant_id:
            tenant = Tenant.active_objects.filter(id=tenant_id).first()
            if not tenant:
                tenant_not_found = True
        
        tenant_slug = request.GET.get("tenant_slug")
        if not tenant and tenant_slug:
            tenant = Tenant.active_objects.filter(slug=tenant_slug).first()
            if not tenant:
                tenant_not_found = True
        
        host = request.get_host()
        config_host = get_app_config().get_host(schema=False)
        if host.endswith(config_host):
            slug = host[:-len(config_host)].rstrip('.')
            if not tenant and slug:
                tenant = Tenant.active_objects.filter(slug=slug).first()
                if not tenant:
                    tenant_not_found = True
        
        if not tenant:
            if tenant_not_found:
                raise Exception('tenant not found for request: {request.path}')
            else:
                tenant = Tenant.platform_tenant()

        request.tenant = tenant
        request.operation_id = self.get_operation_id(request)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response

    def get_operation_id(self, request):
        view_func, _, _ = resolve(request.path)
        try:
            klass = view_func.__self__
            operation, _ = klass._find_operation(request)
            return operation.operation_id or klass.api.get_openapi_operation_id(operation)
        except:
            return ''
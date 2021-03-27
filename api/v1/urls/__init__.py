import copy
from django.urls.resolvers import URLPattern
from django.urls.resolvers import RoutePattern, URLResolver
from . import (
    tenant,
    app,
    webhook,
    user,
    group,
    permission,
    extension,
    external_idp,
    authorization_server,
    jsonp,
    login,
)

urlpatterns = []

from runtime import get_app_runtime


runtime = get_app_runtime()

# @TODO: check passed url
global_urlpatterns = runtime.urlpatterns.get('global', None)
if global_urlpatterns is not None:
    urlpatterns += global_urlpatterns


tenant_urlpatterns = runtime.urlpatterns.get('tenant', None)
if tenant_urlpatterns is not None:
    u: URLPattern
    a = []
    for u in tenant_urlpatterns:
        print(u, u.pattern, u.name, type(u.pattern), dir(u))    
        uu = copy.deepcopy(u)
        a.append(uu)

    urlpatterns += a
    # urlpatterns += tenant_urlpatterns


local_urlpatterns = runtime.urlpatterns.get('local', None)
if local_urlpatterns is not None:
    urlpatterns += local_urlpatterns


urlpatterns += login.urlpatterns
urlpatterns += tenant.router.urls
urlpatterns += jsonp.urlpatterns
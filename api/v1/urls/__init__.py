import auth_rules
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
    marketplace,
    extension,
    external_idp,
    authorization_agent,
    authorization_server,
    jsonp,
    login_page,
    storage,
    sms,
    migration,
    setup,
    authcode,
    config,
    system,
    email,
    device,
    login_register_config,
    auth_rule,
    other_auth_factor,
    login,
    register,
    reset_password,
    log,
    statistics,
    data_sync,
)
from runtime import get_app_runtime


urlpatterns = []


runtime = get_app_runtime()
# @TODO: check passed url
global_urlpatterns = runtime.urlpatterns.get('global', None)
if global_urlpatterns is not None:
    urlpatterns += global_urlpatterns
else:
    print('registered global urlpatterns...')


tenant_urlpatterns = runtime.urlpatterns.get('tenant', None)

if tenant_urlpatterns is not None:
    u: URLPattern
    a = []
    for u in tenant_urlpatterns:
        uu = copy.deepcopy(u)
        a.append(uu)

    urlpatterns += a
    urlpatterns += tenant_urlpatterns

local_urlpatterns = runtime.urlpatterns.get('local', None)
if local_urlpatterns is not None:
    urlpatterns += local_urlpatterns


urlpatterns += login_page.urlpatterns
urlpatterns += tenant.router.urls
urlpatterns += jsonp.urlpatterns
urlpatterns += storage.urlpatterns
urlpatterns += sms.urlpatterns
urlpatterns += migration.urlpatterns
urlpatterns += tenant.urlpatterns
urlpatterns += setup.urlpatterns

urlpatterns += marketplace.router.urls
urlpatterns += user.urlpatterns
urlpatterns += marketplace.urlpatterns
urlpatterns += authcode.urlpatterns
urlpatterns += config.urlpatterns
urlpatterns += system.urlpatterns
urlpatterns += email.urlpatterns
urlpatterns += app.urlpatterns
urlpatterns += login_register_config.router.urls
urlpatterns += other_auth_factor.router.urls
urlpatterns += device.urlpatterns
urlpatterns += auth_rule.urlpatterns

urlpatterns += login.urlpatterns
urlpatterns += register.urlpatterns
urlpatterns += reset_password.urlpatterns
urlpatterns += permission.urlpatterns
urlpatterns += statistics.urlpatterns

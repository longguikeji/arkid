from django.views import View
from django.shortcuts import render,redirect
from django.urls import reverse
from app.models import App
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

@method_decorator(never_cache, name='dispatch')
class MockLogin(View):
    """
    SAML2.0  IDP默认页面
    """
    def get(self, request,tenant_uuid,app_id):    # pylint: disable=no-self-use
        return render(
            request,
            "saml2idp/dev/mock_login.html",
            context={
                "token_url": reverse("api:login"),
                "next": reverse("api:saml2idp:dev_index", args=[tenant_uuid, app_id])
            }
        )
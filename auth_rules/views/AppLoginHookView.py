
from django.views import View
from app.models import App
from auth_rules.models import TenantAuthRule
from runtime import get_app_runtime


class AppLoginHookView(View):

    def get(self,request,*args, **kwargs):
        app_id = request.GET.get("app_id",None)
        assert(app_id is not None)
        print(request,app_id)

        app = App.active_objects.get(id=app_id)

        excludes = request.GET.get("excludes",None)

        rules = TenantAuthRule.active_objects.filter()
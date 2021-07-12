from django.shortcuts import render
from django.views import View
from app.models import App

class HookView(View):

    def get(self, request, tenant_uuid):    # pylint: disable=no-self-use
        """
        调用sso url 前中转
        """
        app_id = request.GET.get("app_id")
        spauthn = request.GET.get("spauthn")
        app = App.active_objects.get(id=app_id)
        return render(request, 'dev/hook.html', context={'sso_url': app.data["sso_url"],"spauthn":spauthn})

from django.views import View


class AppLoginHookView(View):

    def get(self,request,*args, **kwargs):
        app_id = request.GET.get("app_id",None)
        assert(app_id is not None)

        print(request,app_id)
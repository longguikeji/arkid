from datetime import datetime
import json
from django import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from app.models import App
from ..models import AppSubscribeRecord


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
@method_decorator(login_required, "dispatch")
class AppSubscribe(views.View):

    def post(self, request, tenant_uuid, app_id):
        try:
            if hasattr(request, "data"):
                data = request.data
            elif hasattr(request, "body"):
                data = json.loads(request.body)
            else:
                data = request.POST
        except Exception as err:
            print(err)
            data = request.GET
        app =  App.active_objects.get(id=app_id)
        user = request.user
        status = data.get("status", True)

        if hasattr(app, "subscribed_record"):
            if status:
                app.subscribed_record.users.add(user)
            else:
                app.subscribed_record.users.remove(user)
            app.subscribed_record.save()
        else:
            # 尚未有记录
            record = AppSubscribeRecord(
                app = app,
            )
            if status:
                record.users.add(user)
            record.save()

        return JsonResponse(
            data={
                "status": 200
            }
        )

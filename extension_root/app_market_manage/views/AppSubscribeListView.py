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
from django.contrib.auth import get_user_model
User = get_user_model()


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class AppSubscribeList(views.View):

    def get(self, request, tenant_uuid, user_id):
        user = User.active_objects.get(uuid=user_id)
        print(user)
        app_list = App.active_objects.filter(tenant__uuid=tenant_uuid).all()

        res_data = []

        for app in app_list:
            if hasattr(app, "subscribed_record"):
                res_data.append({
                    "name": app.name,
                    "id": app.uuid,
                    "value": user in app.subscribed_record.users.all()
                })
            else:
                record = AppSubscribeRecord(
                    app=app,
                )
                record.save()
                res_data.append({
                    "name": app.name,
                    "id": app.uuid,
                    "value": False
                })

        return JsonResponse(
            data={
                "data": res_data,
                "status": 200
            }
        )

from datetime import datetime
import json
from django import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.http.response import JsonResponse
from common.app_check import AppLoginRequiredMixin
from ..models import Message
from inventory.models import User


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class MessageAdd(AppLoginRequiredMixin, views.View):

    def post(self, request, tenant_uuid, app_id):
        print(request.app)

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

        user_id = data.get("user_id", None)
        user = User.active_objects.get(
            id=user_id
        )
        message = Message(
            app=request.app,
            title=data.get("title"),
            time=data.get("time", datetime.now()),
            content=data.get("content"),
            user=user
        )
        message.save()

        return JsonResponse(
            data={
                "status": 200
            }
        )

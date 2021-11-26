from datetime import datetime
import json
from django import views
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from app.models import App
from inventory.models import Tenant
from ..models import AppSubscribeRecord
from api.v1.serializers.app import AppBaseInfoSerializer
from django.contrib.auth import get_user_model
User = get_user_model()


@method_decorator(never_cache, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class SubscribeAppList(views.View):

    def get(self, request, tenant_uuid, user_id):
        tenant = Tenant.active_objects.get(uuid=tenant_uuid)
        user = User.objects.get(uuid=user_id)
        print(user)
        data = []
        if hasattr(user, "app_subscribed_records"):
            apps = [record.app for record in user.app_subscribed_records.filter(app__tenant=tenant).all() if (
                not record.app.is_del and record.app.is_active)]
            data = AppBaseInfoSerializer(apps, many=True).data

        return JsonResponse(
            data={
                "status": 200,
                "data": data
            }
        )

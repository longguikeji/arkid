"""
登录
"""
import json
import re
from django.views import View
from rest_framework.views import APIView
from django.http.response import JsonResponse
from inventory.models import Group, User, Tenant
from extension.models import Extension
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name="dispatch")
class Login(View):
    def post(self,request):
        d_data = json.loads(request.body)
        user = User.active_objects.get(username=d_data["username"])
        password = d_data["password"]
        if user.check_password(password):
            token = user.refresh_token()
            return_data = {"token": token.key, "user_uuid": user.uuid.hex}
            return JsonResponse(
                data={
                    "error":"0",
                    "data":return_data
                }
            )
        else:
            return JsonResponse(
                data={
                    "error":"1",
                    "message":"not correct username/password"
                }
            )
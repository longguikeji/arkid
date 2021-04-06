from rest_framework import views
from ..serializers import loginpage as lp
from common import loginpage as model
from openapi.utils import extend_schema
from django.http.response import JsonResponse
from api.v1.views.login import LoginView, MobileLoginView

@extend_schema(tags = ['login page'])
class LoginPage(views.APIView):

    @extend_schema(
        responses=lp.LoginPagesSerializer
    )
    def get(self, request):
        tenant_id = request.query_params.get('tenant', None)
        if tenant_id:
            pass
        else:
            data = model.LoginPages()
            data.addForm(model.LOGIN, LoginView().login_form())
            data.addForm(model.LOGIN, MobileLoginView().login_form())
            data.addBottom(model.LOGIN, model.Button(
                prepend='还没有账号，',
                label='立即注册',
                gopage='register'
            ))
            data.addBottom(model.LOGIN, model.Button(
                label='忘记密码',
                gopage='password'
            ))
        
        pages = lp.LoginPagesSerializer(data=data)
        pages.is_valid()
        return JsonResponse(pages.data)
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema
from .serializers import AliyunConfigResponseSerializer, AliyunSendSMSSerializer

@extend_schema(tags=['config'])
class AliyunSmsView(APIView):

  @extend_schema(
    summary='获取配置',
    responses=AliyunConfigResponseSerializer,
  )
  def get(self, request, format=None):
    return Response(request)

  @extend_schema(
    summary='更新配置',
    request=AliyunConfigResponseSerializer,
  )
  def put(self, request, format=None):
    return Response('OK')

@extend_schema(tags=['send_sms'])
class AliyunSmsSendView(APIView):

  @extend_schema(
    summary='发送短信',
    request=AliyunSendSMSSerializer,
  )
  def post(self, request, format=None):
    return Response('send sms ok!')
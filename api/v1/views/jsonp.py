from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.http import HttpRequest, HttpResponse
import requests
from urllib import parse
import json

class JsonpView(APIView):
    
    def get(self, request:Request, format=None):
        path = request.query_params.get('url')
        method = request.query_params.get('method')
        data = parse.parse_qs(request.query_params.get('data'))
        callback = request.query_params.get('callback')

        _request:HttpRequest = request._request
        
        url = _request.build_absolute_uri(path)
        if method == 'get':
            response = requests.get(
                url = url, 
                params = data, 
            )
        elif method == 'post':
            response = requests.post(
                url=url,
                data=data,
            )
        else:
            return HttpResponse('not allowed http method, only: get, post')
        response = HttpResponse(callback+'('+response.text+')', content_type='text/javascript')
        return response
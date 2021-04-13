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
        headers = {}

        token = data.get('token')
        if token:
            headers['Authorization'] = 'token ' + token[0]

        _request:HttpRequest = request._request
        
        url = _request.build_absolute_uri(path)
        if method == 'get':
            response = requests.get(
                url = url, 
                params = data, 
                headers = headers,
            )
        elif method == 'post':
            response = requests.post(
                url=url,
                data=data,
                headers = headers,
            )
        else:
            return HttpResponse('not allowed http method, only: get, post')
        response = HttpResponse(callback+'('+response.text+')', content_type='text/javascript')
        return response
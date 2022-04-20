from urllib.parse import urlsplit
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from arkid.core.api import api
from django.http import HttpResponse
from ninja.responses import Response


class Redoc(View):
    def get(self, request, *args, **kwargs):    # pylint: disable=no-self-use unused-argument        
        # openapi_url = reverse('api/v1/openapi.json')
        # return render(request, 'redoc.html', context={"openapi_url":openapi_url})
        http = urlsplit(request.build_absolute_uri(None)).scheme
        #获得当前的HTTP或HTTPS
        host = request.META['HTTP_HOST']
        #获取当前域名
        openapi_url = http + '://' + host + '/api/v1/openapi_redoc.json'
        # openapi_url = reverse('api/v1/openapi_redoc.json')
        return render(request, 'redoc.html', context={'openapi_url':openapi_url})


class RedocOpenAPI(View):
    def get(self, request, *args, **kwargs):    # pylint: disable=no-self-use unused-argument        
        schema = api.get_openapi_schema()
        # delete discriminator
        for value in schema['components']['schemas'].values():
            value.pop('discriminator', None)
        return Response(schema)


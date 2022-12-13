from urllib.parse import urlsplit
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from arkid.core.api import api
from django.http import HttpResponse
from ninja.responses import Response
from arkid.core.translation import reset_lang_maps

# lang_maps = reset_lang_maps()


class Redoc(View):
    def get(
        self, request, *args, **kwargs
    ):  # pylint: disable=no-self-use unused-argument
        # openapi_url = reverse('api/v1/openapi.json')
        # return render(request, 'redoc.html', context={"openapi_url":openapi_url})
        http_host = request._current_scheme_host
        # 获得当前的HTTP或HTTPS
        # host = request.META['HTTP_HOST']
        # 获取当前域名
        openapi_url = '/api/v1/openapi_redoc.json'
        # openapi_url = http + '://' + host + '/api/v1/openapi.json'
        # openapi_url = reverse('api/v1/openapi_redoc.json')
        language = request.GET.get('FrontendLanguage')
        if language:
            openapi_url = openapi_url + f"?FrontendLanguage={language}"
    
        return render(request, 'redoc.html', context={'openapi_url': openapi_url})



def translate_schema(schema,lang_maps):
    if isinstance(schema,str):
        if schema in lang_maps.keys():
            return lang_maps[schema]
        else:
            return schema
    elif isinstance(schema,dict):
        for key in schema.keys():
            if key in ["translation"]:
                continue
            schema[key] = translate_schema(schema[key],lang_maps)
    elif isinstance(schema,list):
        for index in range(len(schema)):
            if isinstance(schema[index],dict) or isinstance(schema,str):
                schema[index] = translate_schema(schema[index],lang_maps)

    return schema
class RedocOpenAPI(View):
    """专门为Redoc准备的OpenAPI接口

    因为redoc无法处理多层嵌套的discriminator的显示,只能在此过滤掉
    为了兼容一层discriminator的显示，特地设计了“depth”这个值，放到了多层discriminator的结构中，以保证显示的正确

    """

    def get(
        self, request, *args, **kwargs
    ):  # pylint: disable=no-self-use unused-argument
        schema = api.get_openapi_schema()
        # delete discriminator
        for value in schema['components']['schemas'].values():
            if 'depth' in value and value['depth'] > 0:
                value.pop('discriminator', None)
        
        lang_maps = schema["translation"]
        language = request.GET.get('FrontendLanguage','简体中文')
        if language in lang_maps.keys() and lang_maps[language]:        
            schema = translate_schema(schema,lang_maps[language])
        
        return Response(schema)

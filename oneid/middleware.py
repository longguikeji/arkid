'''
middleware
'''

from django.utils.module_loading import import_string

from oneid_meta.models import MiddlewarePlugin


def dynamic_custom_middleware(get_response):
    '''
    插入 自定义的 middleware plugin
    TODO: 目前改动后需要重启才能生效；
    '''

    plugins = MiddlewarePlugin.valid_objects.filter(is_active=True).order_by('order_no')
    middlewares = []
    for plugin in plugins:
        try:
            func = import_string(plugin.import_path)
            middlewares.append(func)
        except ImportError:
            plugin.kill()
    middlewares.reverse()

    def middleware(request):
        '''
        do nothing
        '''
        return get_response(request)

    for wrapper in middlewares:
        middleware = wrapper(middleware)

    return middleware

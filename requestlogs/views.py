from rest_framework.views import exception_handler as drf_exception_handler

from requestlogs import get_requestlog_entry


def exception_handler(exc, context):
    drf_request = context['request']
    get_requestlog_entry(drf_request).drf_request = drf_request
    return drf_exception_handler(exc, context)

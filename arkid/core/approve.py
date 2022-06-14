import io
from arkid.common.logger import logger
from django.core.handlers.wsgi import WSGIRequest
from django.urls import resolve
from arkid.core.models import ApproveRequest


def restore_approve_request(approve_request):
    environ = approve_request.environ
    body = approve_request.body
    environ["wsgi.input"] = io.BytesIO(body)
    request = WSGIRequest(environ)
    request.tenant = approve_request.action.tenant
    request.user = approve_request.user
    view_func, args, kwargs = resolve(request.path)
    klass = view_func.__self__
    operation, _ = klass._find_operation(request)
    response = operation.run(request, **kwargs)
    logger.info(
        f'Restore Request: {approve_request.user.username}:{approve_request.action.method}:{approve_request.action.path}'
    )
    return response


def create_approve_request(http_request, user, approve_action):

    environ = http_request.environ
    environ.pop("wsgi.input")
    environ.pop("wsgi.errors")
    environ.pop("wsgi.file_wrapper")
    approve_request = ApproveRequest.valid_objects.create(
        action=approve_action,
        user=user,
        environ=environ,
        body=http_request.body,
    )
    return approve_request

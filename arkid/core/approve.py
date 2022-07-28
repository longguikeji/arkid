import io
from arkid.common.logger import logger
from django.core.handlers.wsgi import WSGIRequest
from django.urls import resolve
from arkid.core.models import ApproveRequest, ApproveAction
from arkid.extension.models import Extension
import copy

def restore_approve_request(approve_request):
    environ = copy.deepcopy(approve_request.environ)
    body = approve_request.body
    environ["wsgi.input"] = io.BytesIO(body)
    request = WSGIRequest(environ)
    request.user = approve_request.user
    request.tenant = approve_request.user.tenant
    view_func, args, kwargs = resolve(request.path)
    klass = view_func.__self__
    operation = klass._find_operation(request)
    request.operation_id = operation.operation_id or klass.api.get_openapi_operation_id(operation)
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


def create_approve_action(
    name,
    path,
    method,
    description=None,
    extension=None,
    tenant=None,
):
    """
    如果tenant为None， 则为平台级别审批动作，对所有租户起作用
    """
    action = ApproveAction.valid_objects.filter(
        path=path, method=method, tenant=tenant
    ).first()
    if action:
        return action

    if not extension:
        extension = Extension.valid_objects.get(
            package='com.longgui.approve.system.arkid'
        )   

    action = ApproveAction.valid_objects.create(
        name=name,
        description=description,
        path=path,
        method=method,
        extension=extension,
        tenant=tenant,
    )
    return action

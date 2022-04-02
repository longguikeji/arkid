from .api import api

from ninja import Schema, Query
from arkid.core.event import TagSignal, dispatch, register, Event

class UserIn(Schema):
    username: str
    password: str

UserIn.use1 = ''

class UserOut(Schema):
    id: int
    idx: int
    # username: str


# from pydantic import BaseModel
# class ApiEventData(BaseModel):
#     request: any
#     response: dict


class RequestResponse:
    def __init__(self, request, response) -> None:
        self.request = request
        self._response = response

    @property
    def response(self):
        return self._response


def operation():
    from functools import partial

    def replace_view_func(operation):
        tag = api.get_openapi_operation_id(operation)
        register(
            tag = tag,
            name = operation.summary,
            description = operation.description,
            # data_model = ApiEventData
        )

        old_view_func = operation.view_func
        def func(request, *params, **kwargs):
            response = old_view_func(request=request, *params, **kwargs)
            # copy request
            dispatch(Event(tag, 'tenant', RequestResponse(request, response)))
            return response
        operation.view_func = func

    def decorator(view_func):
        old_ninja_contribute_to_operation = getattr(view_func, '_ninja_contribute_to_operation', None)
        def ninja_contribute_to_operation(operation):
            if old_ninja_contribute_to_operation:
                old_ninja_contribute_to_operation(operation)
            replace_view_func(operation)
            
        view_func._ninja_contribute_to_operation = partial(
            ninja_contribute_to_operation
        )
        return view_func

    return decorator

@api.get("/users/", response=UserOut, auth=None)
@operation()
def create_user(request, data: UserIn = Query(...)):
    user = {'id': 1}
    return user


from django.dispatch import Signal, receiver
from django.core.signals import request_finished
@receiver(request_finished)
def request_finished_test(sender, **kwargs):
    print('request_finished_test', sender, kwargs)

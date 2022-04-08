from typing import Any
from arkid.core.api import api, operation

from ninja import Schema, Query
from arkid.core.event import dispatch_event, register_event, Event

class UserIn(Schema):
    username: str
    password: str

UserIn.use1 = ''

class UserOut(Schema):
    id: int
    # username: str
    
UserOut.schema()
class ApiEventData(Schema):
    request: Any
    response: UserOut
    
@api.get("/users/", response=UserOut, auth=None)
@operation(ApiEventData)
def create_user(request, data: UserIn = Query(...)):
    user = {'id': 1,"username":_("data")}
    return user


from django.dispatch import Signal, receiver
from django.core.signals import request_finished
@receiver(request_finished)
def request_finished_test(sender, **kwargs):
    print('request_finished_test', sender, kwargs)

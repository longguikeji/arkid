from arkid.core.api import api
from ninja import Schema

class Message(Schema):
    detail: str

def permission_check(func):
    from functools import wraps
    @wraps(func)
    def decorator(*args, **kwargs):
        func.view_func = func
        # 取得 operation_id
        operation_id = api.get_openapi_operation_id(func)
        result = func(*args, **kwargs)
        return result
    return decorator
    
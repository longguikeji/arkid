import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'arkid.settings')
django.setup()
from arkid.config import get_app_config
from arkid.core.models import ApiPermission
from .celery import app
import requests, uuid

@app.task
def update_permission():
    host = get_app_config().get_host()
    api_info = '{}/api/v1/openapi_redoc.json'.format(host)
    permission_task(None, api_info)


def permission_task(app_temp, api_info):
    response = requests.get(api_info)
    response = response.json()
    paths = response.get('paths')
    path_keys = paths.keys()
    info = response.get('info')
    title = info.get('title')
    base_code = title
    old_permissions = ApiPermission.valid_objects.filter(tenant=None,
      app=app_temp,
      category='api',
      is_system=True,
      base_code=base_code)
    for old_permission in old_permissions:
        old_permission.is_update = False
        old_permission.save()
    else:
        for path_key in path_keys:
            item = paths.get(path_key)
            item_keys = item.keys()
            for item_key in item_keys:
                request_obj = item.get(item_key)
                request_type = item_key
                request_url = path_key
                summary = request_obj.get('summary', '')
                operation_id = request_obj.get('operationId')
                codename = 'api_{}'.format(uuid.uuid4())
                permission, is_create = ApiPermission.objects.get_or_create(category='api',
                  is_system=True,
                  app=app_temp,
                  is_del=False,
                  operation_id=operation_id,
                  base_code=base_code)
                if is_create is True:
                    permission.codename = codename
                permission.name = summary
                permission.request_url = request_url
                permission.request_type = request_type
                permission.is_update = True
                permission.save()

        else:
            ApiPermission.valid_objects.filter(tenant=None,
              app=app_temp,
              category='api',
              is_system=True,
              base_code=base_code,
              is_update=False).delete()
import json
from tenant.models import Tenant
from requestlogs.storages import logger
from requestlogs.storages import BaseStorage
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.encoders import JSONEncoder
from .models import Log


class CustomLoggingStorage(BaseStorage):
    def store(self, entry):
        data = self.prepare(entry)

        tenant_uuid = data["tenant"]["uuid"]
        tenant = Tenant.objects.filter(uuid=tenant_uuid).first()

        if tenant:
            # message = json.dumps(data, cls=JSONEncoder)
            # logger.debug(message)

            log = Log.valid_objects.create(tenant=tenant, data=data)
            log.save()

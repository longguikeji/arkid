from lib.dynamic_fields_model_serializer import DynamicFieldsModelSerializer
from inventory.models import Permission


class PermissionSerializer(DynamicFieldsModelSerializer):

    class Meta:
        model = Permission

        fields = (
            'uuid',
            'name',
            'codename',
        )

from drf_spectacular.openapi import AutoSchema
from . import custom
AutoSchema.get_operation = custom.AutoSchema.get_operation
AutoSchema.get_action = custom.AutoSchema.get_action
AutoSchema.get_action_type = custom.AutoSchema.get_action_type
AutoSchema.get_roles = custom.AutoSchema.get_roles
AutoSchema._get_serializer_field_meta = custom.AutoSchema._get_serializer_field_meta
AutoSchema._map_serializer_field = custom.AutoSchema._map_serializer_field

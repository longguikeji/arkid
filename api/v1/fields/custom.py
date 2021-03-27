from rest_framework import serializers
from drf_spectacular.drainage import set_override, get_override
from drf_spectacular.utils import extend_schema_field

def create_foreign_field(field_cls):

    @extend_schema_field(
        field = {
            'format': 'foreign',
        }
    )
    class ForeignField(field_cls):
        _field_meta = {}

        def __init__(self, model_cls, field_name, path, method, page_type, **kwargs):
            field = get_override(self, 'field', {})
            field['model'] = model_cls.__name__
            field['field'] = field_name
            field['path'] = path
            field['method'] = method
            field['pageType'] = page_type
            if 'source' in kwargs:
                field['source'] = kwargs['source']

            for k, v in kwargs.items():
                if isinstance (v,(str,int,list,bool,dict,float)):
                    field[k] = v

            set_override(self, 'field', field)
            super().__init__(**kwargs)

    return ForeignField


def create_foreign_key_field(field_cls):

    @extend_schema_field(
        field={
            'format':'foreign_key',
        }
    )
    class ForeignKeyField(create_foreign_field(field_cls)):
        def __init__(self, model_cls, field_name, **kwargs):
            print(kwargs)
            super().__init__(model_cls, field_name, **kwargs)

    return ForeignKeyField

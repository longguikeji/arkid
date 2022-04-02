from typing import Any, Dict, Optional
from pydantic.fields import ModelField


def add_fields(cls, **field_definitions: Any):
    new_fields: Dict[str, ModelField] = {}
    new_annotations: Dict[str, Optional[type]] = {}

    for f_name, f_def in field_definitions.items():
        if isinstance(f_def, tuple):
            try:
                f_annotation, f_value = f_def
            except ValueError as e:
                raise Exception(
                    'field definitions should either be a tuple of (<type>, <default>) or just a '
                    'default value, unfortunately this means tuples as '
                    'default values are not allowed'
                ) from e
        else:
            if isinstance(f_def, type):
                f_annotation, f_value = f_def, None
            else:
                f_annotation, f_value = None, f_def
        if f_value is Ellipsis:
            f_value = None

        if f_annotation:
            new_annotations[f_name] = f_annotation

        new_fields[f_name] = ModelField.infer(name=f_name, value=f_value, annotation=f_annotation, class_validators=None, config=cls.__config__)

    cls.__fields__.update(new_fields)
    cls.__annotations__.update(new_annotations)
    cls.__schema_cache__.clear()
		
	
def remove_fields(cls, fields: Any):
    if isinstance(fields, list) or  isinstance(fields, tuple):
        for field in fields:
            cls.__fields__.pop(field, None)
            cls.__annotations__.pop(field, None)
    else:
        cls.__fields__.pop(fields)
        cls.__annotations__.pop(fields, None)
    cls.__schema_cache__.clear()


# from pydantic import BaseModel
# class Model(BaseModel):
#     foo: str

# # add_fields(Model, bar=(str, ...), baz='qwe')
# add_fields(Model, bar=(str), baz='qwe')
# print(Model.schema())
# remove_fields(Model, 'bar')
# print(Model.schema())

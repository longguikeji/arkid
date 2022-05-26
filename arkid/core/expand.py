from django.db import models
from arkid.core.translation import gettext_default as _
from django.db import transaction
from django.db.models import F

def create_expand_abstract_model(model, package, model_name):
    class TempModel(model):
        class Meta:
            abstract = True
        
        target = models.ForeignKey(
            model.foreign_key,
            blank=True,
            default=None,
            on_delete=models.PROTECT,
            related_name=package.replace('.','_')+'_'+model_name,
        )
    return TempModel

field_expand_map = {}
def register_expand_field(table, field, extension_name, extension_model_cls, extension_table, extension_field):
    data = (
            table,
            field,
            extension_name,
            extension_model_cls,
            extension_table,
            extension_field,
        )
    if table not in field_expand_map:
        field_expand_map[table] = []
    field_expand_map[table].append(data)
    return data

def unregister_expand_field(data):
    field_expand_map[data[0]].remove(data)

class ExpandManager(models.Manager):
    """ Enables changing the default queryset function. """

    def get_queryset(self, filters:dict={}):

        table_name = self.model._meta.db_table
        
        field_expands = field_expand_map.get(table_name,{})
        queryset = self.model.objects
        
        annotate_params = {}
        related_names = []
        values = []
        for field in self.model._meta.fields:
            if field.name == 'password':
                continue
            values.append(field.name)
            
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            related_name = extension_name+'_'+extension_model_cls._meta.object_name
            related_names.append(related_name)
            annotate_params[field] = F(related_name+'__'+extension_field)
            values.append(field)
        
        return queryset.annotate(**annotate_params).select_related(*related_names).values(*values)

class ExpandModel(models.Model):

    class Meta:
        abstract = True

    expand_objects = ExpandManager()

    @transaction.atomic()
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        table_name = self._meta.db_table
        # queryset = FieldExpandMap.objects.filter(table=table_name)
        if table_name not in field_expand_map:
            return
        
        field_expands = field_expand_map[table_name]

        extension_tables = {}
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            if hasattr(self, field):
                if extension_table not in extension_tables:
                    extension_model_obj = extension_model_cls()
                    extension_model_obj.target = self
                    extension_tables[extension_table] = extension_model_obj
                else:
                    extension_model_obj = extension_tables[extension_table]

                setattr(extension_model_obj, extension_field, getattr(self, field))

        for extension_model_obj in extension_tables.values():
            extension_model_obj.save()

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        table_name = self._meta.db_table
        # queryset = FieldExpandMap.objects.filter(table=table_name)
        if table_name not in field_expand_map:
            return
        field_expands = field_expand_map[table_name]

        extension_tables = {}
        for table, field,extension_name,extension_model_cls,extension_table,extension_field  in field_expands:
            if extension_table not in extension_tables:
                extension_model_obj = extension_model_cls()
                extension_tables[extension_table] = extension_model_obj
            else:
                extension_model_obj = extension_tables[extension_table]

            if hasattr(self, field):
                setattr(extension_model_obj, extension_field, getattr(self, field))

        for obj in extension_tables.values():
            obj.delete()


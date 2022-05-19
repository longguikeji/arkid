from webbrowser import get
from django.db import models
from arkid.common.model import BaseModel
from arkid.core.translation import gettext_default as _
from django.db import transaction


class TenantExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    tenant = models.ForeignKey(
        'core.Tenant',
        blank=False,
        on_delete=models.PROTECT,
    )


class UserExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    user = models.ForeignKey(
        'core.User',
        blank=False,
        on_delete=models.PROTECT,
    )


class UserGroupExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    user_group = models.ForeignKey(
        'core.UserGroup',
        blank=False,
        on_delete=models.PROTECT,
    )


class AppExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    app = models.ForeignKey(
        'core.App',
        blank=False,
        on_delete=models.PROTECT,
    )


class AppGroupExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    app_group = models.ForeignKey(
        'core.AppGroup',
        blank=False,
        on_delete=models.PROTECT,
    )


class PermissionExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    permission = models.ForeignKey(
        'core.Permission',
        blank=False,
        on_delete=models.PROTECT,
    )


class ApproveExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    approve = models.ForeignKey(
        'core.Approve',
        blank=False,
        on_delete=models.PROTECT,
    )


class TenantConfigExpandAbstract(BaseModel):

    class Meta:
        abstract = True

    tenant_config = models.ForeignKey(
        'core.TenantConfig',
        blank=False,
        on_delete=models.PROTECT,
    )


def map_field(cls, alias=None):
    cls.alias = alias
    return cls


field_expand_map = []



# class FieldExpandMap(BaseModel):

#     class Meta(object):
#         verbose_name = _("字段扩展表")
#         verbose_name_plural = _("字段扩展表")

#     table = models.CharField(max_length=128, blank=False)
#     field = models.CharField(max_length=128, blank=False)
#     extension = models.CharField(max_length=128, blank=False)
#     extension_model = models.CharField(max_length=128, blank=False)
#     extension_table = models.CharField(max_length=128, blank=False)
#     extension_field = models.CharField(max_length=128, blank=False)



class ExpandManager(models.Manager):
    """ Enables changing the default queryset function. """

    def get_queryset(self, filters:dict={}):

        model_name = self.model._meta.model_name
        table_name = self.model._meta.db_table
        # queryset = FieldExpandMap.objects.filter(table=table_name)
        queryset = field_expand_map

        extension_tables = set()
        select_sql = f'Select {table_name}.*'
        join_sql = ""

        for q in queryset:
            select_sql = select_sql + f", {q.extension_table}.{q.extension_field} as {q.field}"
            if q.extension_table not in extension_tables:
                join_sql = join_sql + f" LEFT JOIN {q.extension_table} on {table_name}.id = {q.extension_table}.{model_name}_id "
                extension_tables.add(q.extension_table)
        
        where_condition = ""
        if filters:
            where_condition = f" WHERE {' AND '.join([f'{k} = {v}' for k,v in filters.items()])}"

        sql = select_sql  + f" FROM {table_name} " + join_sql + f" {where_condition} ORDER BY {table_name}.id"
        queryset = self.model.objects.raw(sql)
        return queryset

    def make_filters(self,filters):
        new_filters = {}
        for k,v in filters.items():
            key = f"{self.model._meta.db_table}.{k}"
            if isinstance(v,str):
                new_filters[key] = f"'{v}'"
            else:
                new_filters[key] = f"{v}"
        return new_filters

    def get(self, **filters):
        filters = self.make_filters(filters)
        queryset = self.get_queryset(filters)
        return list(queryset)[0] if queryset else None

    def filter(self,**filters):
        filters = self.make_filters(filters)
        queryset = self.get_queryset(filters)
        return queryset


class ExpandModel(models.Model):

    class Meta:
        abstract = True

    expand_objects = ExpandManager()

    @transaction.atomic()
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        table_name = self._meta.db_table
        # queryset = FieldExpandMap.objects.filter(table=table_name)
        queryset = field_expand_map

        extension_tables = {}
        for q in queryset:
            if hasattr(self, q.field):
                if q.extension_table not in extension_tables:
                    extension_model_obj = q.extension_model_cls()
                    extension_model_obj.user = self
                    extension_tables[q.extension_table] = extension_model_obj
                else:
                    extension_model_obj = extension_tables[q.extension_table]

                setattr(extension_model_obj, q.extension_field, getattr(self, q.field))

        for extension_model_obj in extension_tables.values():
            extension_model_obj.save()

    @transaction.atomic()
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        table_name = self._meta.db_table
        # queryset = FieldExpandMap.objects.filter(table=table_name)
        queryset = field_expand_map

        extension_tables = {}
        for q in queryset:
            if q.extension_table not in extension_tables:
                extension_model_obj = q.extension_model_cls()
                extension_tables[q.extension_table] = extension_model_obj
            else:
                extension_model_obj = extension_tables[q.extension_table]

            if hasattr(self, q.field):
                setattr(extension_model_obj, q.extension_field, getattr(self, q.field))

        for obj in extension_tables.values():
            obj.delete()


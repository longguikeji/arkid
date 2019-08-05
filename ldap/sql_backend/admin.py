from django.contrib import admin

from ldap.sql_backend.models import (
    LDAPOCMappings,
    LDAPAttrMapping,
    LDAPEntry,
    LDAPEntryObjectclasses,
)


class LDAPOCMappingsAdmin(admin.ModelAdmin):
    pass


class LDAPAttrMappingAdmin(admin.ModelAdmin):
    pass


class LDAPEntryAdmin(admin.ModelAdmin):
    pass


class LDAPEntryObjectclassesAdmin(admin.ModelAdmin):
    pass


admin.site.register(LDAPOCMappings, LDAPOCMappingsAdmin)
admin.site.register(LDAPAttrMapping, LDAPAttrMappingAdmin)
admin.site.register(LDAPEntry, LDAPEntryAdmin)
admin.site.register(LDAPEntryObjectclasses, LDAPEntryObjectclassesAdmin)

from abc import abstractmethod
from arkid.core.extension import Extension
from arkid.core.translation import gettext_default as _
from arkid.core.models import App
from arkid.core import api as core_api, event as core_event


class AppProtocolExtension(Extension):
    
    TYPE = "app_protocol"
    
    
    composite_schema_map = {}
    created_composite_schema_list = []
    composite_key = 'app_type'
    composite_model = App
    
    @property
    def type(self):
        return AppProtocolExtension.TYPE
    
    
    def load(self):
        super().load()
        self.listen_event(core_event.CREATE_APP, self.create_app)
        self.listen_event(core_event.UPDATE_APP, self.update_app)
        self.listen_event(core_event.DELETE_APP, self.delete_app)

    def register_app_protocol_schema(self, schema, app_type):
        self.register_config_schema(schema, self.package + '_' + app_type)
        self.register_composite_config_schema(schema, app_type)

    @abstractmethod
    def create_app(self, event):
        pass

    @abstractmethod
    def update_app(self, event):
        pass

    @abstractmethod
    def delete_app(self, event):
        pass
    

from django.db import models
from common.model import BaseModel
from tenant.models import Tenant


class TenantUserConfig(BaseModel):

    class Meta:

        app_label = 'tenantuserconfig'

    tenant = models.ForeignKey(Tenant, on_delete=models.PROTECT)
    data = models.JSONField(blank=True, default=dict)

    def __str__(self) -> str:
        return f'Tenant: {self.tenant.name}'
    
    def save_data(self, tenant):
        self.tenant = tenant
        self.data = {
            'is_edit_fields': [
                {'name':'昵称' , 'en_name':'nickname', 'type':'string'},
                {'name':'电话' , 'en_name':'mobile', 'type':'string'},
                {'name':'邮箱' , 'en_name':'email', 'type':'string'},
                {'name':'职称' , 'en_name':'job_title', 'type':'string'},
                {'name':'姓' , 'en_name':'first_name', 'type':'string'},
                {'name':'名' , 'en_name':'last_name', 'type':'string'},
                {'name':'国家' , 'en_name':'country', 'type':'string'},
                {'name':'城市' , 'en_name':'city', 'type':'string'}
            ],
            'is_logout': False,
            'is_look_token': False,
            'is_manual_overdue_token': False,
            'is_logging_ip': True,
            'is_logging_device': True,
        }
        self.save()

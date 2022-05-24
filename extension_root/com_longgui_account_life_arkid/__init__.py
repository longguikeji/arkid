from arkid.core.extension.account_life import AccountLifeExtension
from arkid.core.extension import create_extension_schema
from arkid.extension.models import TenantExtensionConfig, TenantExtension
import urllib.parse
from pydantic import Field
from arkid.core.translation import gettext_default as _
from ninja import Schema
from api.v1.pages.approve_manage import router as approve_manage_router
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from arkid.common.logger import logger
import json
from .tasks import deactive_expired_user
from .models import UserExpiration
from . import views
from .user_expiration_page import page, edit_page, router
from api.v1.pages.user_manage import router as user_manage_router

package = 'com.longgui.account.life.arkid'


class CronJobSchema(Schema):
    crontab: str = Field(default='0 1 * * *', title=_('Crontab', '定时运行时间'))
    max_retries: int = Field(default=3, title=_('Max Retries', '重试次数'))
    retry_delay: int = Field(default=60, title=_('Retry Delay', '重试间隔(单位秒)'))


class AccountLifeArkIDExtension(AccountLifeExtension):
    def load(self):
        super().load()
        self.register_extend_field(UserExpiration, "expiration_time")
        self.register_account_life_schema(CronJobSchema, "deactive_expired_user_cron")
        self.register_front_pages(page)
        self.register_front_pages(edit_page)
        user_manage_router.children.append(router)

    def create_tenant_config(self, tenant, config, name, type):
        config_created = super().create_tenant_config(
            tenant, config, name=name, type=type
        )
        # self.update_or_create_periodic_task(config_created)
        return config_created

    def update_or_create_periodic_task(self, extension_config):
        crontab = extension_config.config.get('crontab')
        if crontab:
            try:
                crontab = crontab.split(' ')
                crontab.extend(['*'] * (5 - len(crontab)))

                # create CrontabSchedule
                schedule, _ = CrontabSchedule.objects.get_or_create(
                    minute=crontab[0],
                    hour=crontab[1],
                    day_of_week=crontab[2],
                    day_of_month=crontab[3],
                    month_of_year=crontab[4],
                )

                # create PeriodicTask
                PeriodicTask.objects.update_or_create(
                    name=extension_config.id,
                    defaults={
                        'crontab': schedule,
                        'task': deactive_expired_user.name,
                        'args': json.dumps([extension_config.id.hex]),
                        'kwargs': json.dumps(extension_config.config),
                    },
                )
            except Exception as e:
                logger.exception('add celery task failed %s' % e)

    def delete_periodic_task(self, extension_config):
        try:
            # fake delete triggers post_save signal
            PeriodicTask.objects.filter(name=extension_config.id).delete()
        except Exception as e:
            logger.exception('delete celery task failed %s' % e)

    def create_account_life_config(self, event, **kwargs):
        extension_config = event.data
        if extension_config.type != "deactive_expired_user_cron":
            return
        else:
            self.update_or_create_periodic_task(extension_config)

    def update_account_life_config(self, event, **kwargs):
        extension_config = event.data
        if extension_config.type != "deactive_expired_user_cron":
            return
        else:
            self.update_or_create_periodic_task(extension_config)

    def delete_account_life_config(self, event, **kwargs):
        extension_config = event.data
        if extension_config.type != "deactive_expired_user_cron":
            return
        else:
            self.delete_periodic_task(extension_config)


extension = AccountLifeArkIDExtension(
    package=package,
    name='默认账号生命周期管理',
    version='1.0',
    labels='account-life-arkid',
    homepage='https://www.longguikeji.com',
    logo='',
    author='hanbin@jinji-inc.com',
)

import importlib
import copy
import datetime
from arkid.core.extension.statistics import StatisticsExtension
from arkid.core.translation import gettext_default as _
from arkid.extension.models import Extension
from arkid.core.schema import ResponseSchema
from typing import Any, List
from arkid.core.api import api, operation
from arkid.core.constants import NORMAL_USER, TENANT_ADMIN, PLATFORM_ADMIN
from django.db.models import Max, Count, Q
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone


line_chart = {
        'xAxis': {
            'type': 'category',
            'data': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        },
        'yAxis': {
            'type': 'value'
        },
        'legend': {},
        'series': [
            {
                'data': [150, 230, 224, 218, 135, 147, 260],
                'type': 'line',
                'name': '',
            }
        ],
        "title": {
            "text": "用户注册人数变化图",
            "subtext": "过去30天"
        },
    }


class ChartsListOut(ResponseSchema):
    data: List[Any]


class MysqlStatisticsExtension(StatisticsExtension):
    
    def load(self):
        self.register_extension_api()
        self.register_pages()
        self.get_log_model()
        super().load()

    def register_pages(self):
        from .pages import user_statistics, tenant_statistics
        from api.v1.pages.charts_manage import router

        self.register_front_pages([
            user_statistics.page,
            tenant_statistics.page
        ])

        self.register_front_routers(tenant_statistics.router, router)
        self.register_front_routers(user_statistics.router, router)

    def register_extension_api(self):
        self.log_detail_path = self.register_api(
            '/tenant_statistics/', 
            'GET',
            self.get_tenant_statistics_charts, 
            response=ChartsListOut,
            tenant_path=True
        )

        self.user_log_path = self.register_api(
            '/user_statistics/', 
            'GET',
            self.get_user_statistics_charts, 
            response=ChartsListOut,
            tenant_path=True
        )

    def get_log_model(self):
        try:
            ext = Extension.active_objects.filter(package="com.longgui.logging.mysql").first()
            ext_name = str(ext.ext_dir).replace('/','.')
            ext_module = importlib.import_module(ext_name)
            self.log_model = ext_module.models.Log
        except Exception as e:
            print("extension com_longgui_logging_mysql not installed or not activated")

    def gen_tenant_active_chart(self):
        kwargs = {}
        kwargs['created__gte'] = timezone.now() + datetime.timedelta(days=-30)

        qs = self.log_model.objects.filter(**kwargs) \
            .annotate(day=TruncDate('created')) \
            .values('day') \
            .annotate(count=Count('tenant', distinct=True)) \
            .values('day', 'count')  
        res = {r["day"].strftime('%Y-%m-%d'): r["count"] for r in qs}

        xAxis = []
        data = []
        for i in range(29, -1, -1):
            date = str(timezone.localdate() + datetime.timedelta(-i))
            xAxis.append(date)
            data.append(res.get(date, 0))

        chart = copy.deepcopy(line_chart)

        chart['xAxis']['data'] = xAxis
        chart['series'][0]['data'] = data
        chart['series'][0]['name'] = '30天'
        chart['title'] = {
            "text": "活跃租户数量变化图",
            "subtext": "过去30天"
        }

        return chart

    def gen_register_user_chart(self, tenant):
        kwargs = {
            'tenant': tenant,
        }
        kwargs['created__gte'] = timezone.now() + datetime.timedelta(days=-30)
        kwargs['request_path'] = f"/api/v1/tenant/{tenant.id}/register/"
        kwargs['status_code'] = 200

        qs = self.log_model.objects.filter(**kwargs) \
            .annotate(day=TruncDate('created')) \
            .values('day') \
            .annotate(count=Count('id')) \
            .values('day', 'count')  
        res = {r["day"].strftime('%Y-%m-%d'): r["count"] for r in qs}

        xAxis = []
        data = []
        for i in range(29, -1, -1):
            date = str(timezone.localdate() + datetime.timedelta(-i))
            xAxis.append(date)
            data.append(res.get(date, 0))

        chart = copy.deepcopy(line_chart)

        chart['xAxis']['data'] = xAxis
        chart['series'][0]['data'] = data
        chart['series'][0]['name'] = '30天'
        chart['title'] = {
            "text": "用户注册人数变化图",
            "subtext": "过去30天"
        }

        return chart

    def gen_login_user_chart(self, tenant):
        kwargs = {
            'tenant': tenant,
        }
        kwargs['created__gte'] = timezone.now() + datetime.timedelta(days=-30)
        kwargs['request_path'] = f"/api/v1/tenant/{tenant.id}/auth/"
        kwargs['status_code'] = 200

        qs = self.log_model.objects.filter(**kwargs) \
            .annotate(day=TruncDate('created')) \
            .values('day') \
            .annotate(count=Count('id')) \
            .values('day', 'count')  
        res = {r["day"].strftime('%Y-%m-%d'): r["count"] for r in qs}

        xAxis = []
        data = []
        for i in range(29, -1, -1):
            date = str(timezone.localdate() + datetime.timedelta(-i))
            xAxis.append(date)
            data.append(res.get(date, 0))

        chart = copy.deepcopy(line_chart)

        chart['xAxis']['data'] = xAxis
        chart['series'][0]['data'] = data
        chart['series'][0]['name'] = '30天'
        chart['title'] = {
            "text": "用户登录人数变化图",
            "subtext": "过去30天"
        }

        return chart

    def gen_register_user_list(self, tenant):
        kwargs = {
            'tenant': tenant,
        }
        kwargs['request_path'] = f"/api/v1/tenant/{tenant.id}/register/"
        kwargs['status_code'] = 200

        qs = self.log_model.valid_objects.filter(**kwargs).order_by('-created').values('username').distinct()
        res = [x["username"] for x in qs[:10]]

        chart = {
            'data': res,
            'title': {
                "text": "最近注册人列表",
                "subtext": "最近10个"
            },
            'type': 'list',
        }
        return chart

    def gen_login_user_list(self, tenant):
        kwargs = {
            'tenant': tenant,
        }
        kwargs['request_path'] = f"/api/v1/tenant/{tenant.id}/auth/"
        kwargs['status_code'] = 200

        qs = self.log_model.valid_objects.filter(**kwargs).order_by('-created').values('username').distinct()
        res = [x["username"] for x in qs[:10]]

        chart = {
            'data': res,
            'title': {
                "text": "最近登录人列表",
                "subtext": "最近10个"
            },
            'type': 'list',
        }
        return chart

    def get_charts(self, event, **kwargs):
        tenant = event.tenant
        charts = []
        charts.append(self.gen_register_user_chart(tenant))
        charts.append(self.gen_login_user_chart(tenant))
        charts.append(self.gen_register_user_list(tenant))
        charts.append(self.gen_login_user_list(tenant))
        return charts

    @operation(roles=[PLATFORM_ADMIN])
    def get_tenant_statistics_charts(self, request, tenant_id: str):
        '''获取租户统计图表
        '''
        charts = []
        charts.append(self.gen_tenant_active_chart())
        return {"data": charts}

    @operation(roles=[TENANT_ADMIN, PLATFORM_ADMIN])
    def get_user_statistics_charts(self, request, tenant_id: str):
        '''获取用户统计图表
        '''
        tenant = request.tenant
        charts = []
        charts.append(self.gen_register_user_chart(tenant))
        charts.append(self.gen_login_user_chart(tenant))
        return {"data": charts}

extension = MysqlStatisticsExtension()
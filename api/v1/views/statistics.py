import copy
import json
import datetime
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from openapi.utils import extend_schema
from .base import BaseTenantViewSet
from rest_framework_expiring_authtoken.authentication import ExpiringTokenAuthentication

from log.models import Log
from tenant.models import Tenant
from inventory.models import User


@extend_schema(
    roles=['tenant admin', 'global admin'],
    tags=['log']
)
class StatisticsView(BaseTenantViewSet, viewsets.ReadOnlyModelViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [ExpiringTokenAuthentication]

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

    def gen_register_user_chart(self):
        sql = """
            SELECT COUNT(*) as id, cast(created as date) as date
            from log_log
            where data->"$.request.full_path" like "_/api/v1/tenant/%%/user/_" 
            and data->"$.response.status_code"=201
            and DATEDIFF(NOW(), created)<30
            GROUP BY cast(created as date) order by date desc;
            """
        query = Log.objects.raw(sql)
        res = {r.date: r.id for r in query}

        xAxis = []
        data = []
        for i in range(29, -1, -1):
            date = datetime.date.today() + datetime.timedelta(-i)
            xAxis.append(str(date))
            data.append(res.get(date, 0))

        chart = copy.deepcopy(self.line_chart)

        chart['xAxis']['data'] = xAxis
        chart['series'][0]['data'] = data
        chart['series'][0]['name'] = '30天'
        chart['title'] = {
            "text": "用户注册人数变化图",
            "subtext": "过去30天"
        }

        return chart

    def gen_login_user_chart(self):
        sql = """
            SELECT COUNT(*) as id, cast(created as date) as date
            from log_log 
            where data->"$.request.full_path" = "/api/v1/login/"
            and data->"$.response.status_code"=200
            and DATEDIFF(NOW(), created)<30
            GROUP BY cast(created as date) order by date desc;
            """
        query = Log.objects.raw(sql)
        res = {r.date: r.id for r in query}

        xAxis = []
        data = []
        for i in range(29, -1, -1):
            date = datetime.date.today() + datetime.timedelta(-i)
            xAxis.append(str(date))
            data.append(res.get(date, 0))

        chart = copy.deepcopy(self.line_chart)

        chart['xAxis']['data'] = xAxis
        chart['series'][0]['data'] = data
        chart['series'][0]['name'] = '30天'
        chart['title'] = {
            "text": "用户登录人数变化图",
            "subtext": "过去30天"
        }

        return chart

    def gen_register_user_list(self):
        sql = """
            select distinct id from(
                SELECT data->"$.response.data" as id
                from log_log
                where data->"$.request.full_path" like "_/api/v1/tenant/%%/user/_"
                and data->"$.response.status_code"=201
                order by created desc) as b
            limit 10;
            """
        query = Log.objects.raw(sql)
        res = []
        for r in query:
            try:
                d = json.loads(json.loads(r.id))
                username = d["username"]
                if username not in res:
                    res.append(username)
            except:
                pass

        chart = {
            'data': res,
            'title': {
                "text": "最近注册人列表",
                "subtext": "最近10个"
            },
            'type': 'list',
        }
        return chart

    def gen_login_user_list(self):
        sql = """
            select distinct id from(
                SELECT data->"$.request.data" as id
                from log_log
                where data->"$.request.full_path" = "/api/v1/login/"
                and data->"$.response.status_code"=200
                order by created desc) as b
            limit 10;
            """
        query = Log.objects.raw(sql)
        res = []
        for r in query:
            try:
                d = json.loads(json.loads(r.id))
                user_uuid = d["data"]["user_uuid"]
                user = User.objects.filter(uuid=user_uuid).first()
                username = user.username
                if username not in res:
                    res.append(username)
            except:
                pass

        chart = {
            'data': res,
            'title': {
                "text": "最近登录人列表",
                "subtext": "最近10个"
            },
            'type': 'list',
        }
        return chart

    def list(self, request, parent_lookup_tenant):
        charts = []
        charts.append(self.gen_register_user_chart())
        charts.append(self.gen_login_user_chart())
        charts.append(self.gen_register_user_list())
        charts.append(self.gen_login_user_list())
        return Response(charts)

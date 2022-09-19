
from typing import Any, List
from arkid.core.api import api, operation
from arkid.core.constants import *
from arkid.core.schema import ResponseSchema
from arkid.core.translation import gettext_default as _


class TestChartResponse(ResponseSchema):
    data: List[Any] = []


@api.get("/tenant/{tenant_id}/test_chart/", response=TestChartResponse, tags=[_("认证规则")])
@operation(TestChartResponse, roles=[TENANT_ADMIN, PLATFORM_ADMIN])
def get_test_chart(request, tenant_id: str):
    return {
        "data": [
            {
                "xAxis": {
                    "type": "category",
                    "data": [
                        "2022-08-21",
                        "2022-08-22",
                        "2022-08-23",
                        "2022-08-24",
                        "2022-08-25",
                        "2022-08-26",
                        "2022-08-27",
                        "2022-08-28",
                        "2022-08-29",
                        "2022-08-30",
                        "2022-08-31",
                        "2022-09-01",
                        "2022-09-02",
                        "2022-09-03",
                        "2022-09-04",
                        "2022-09-05",
                        "2022-09-06",
                        "2022-09-07",
                        "2022-09-08",
                        "2022-09-09",
                        "2022-09-10",
                        "2022-09-11",
                        "2022-09-12",
                        "2022-09-13",
                        "2022-09-14",
                        "2022-09-15",
                        "2022-09-16",
                        "2022-09-17",
                        "2022-09-18",
                        "2022-09-19"
                    ]
                },
                "yAxis": {
                    "type": "value"
                },
                "legend": {},
                "series": [
                    {
                        "data": [
                            10,
                            0,
                            0,
                            20,
                            0,
                            0,
                            30,
                            0,
                            0,
                            0,
                            50,
                            60,
                            70,
                            80,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0
                        ],
                        "type": "line",
                        "name": "30天"
                    }
                ],
                "title": {
                    "text": "用户注册人数变化图",
                    "subtext": "过去30天"
                }
            },
            {
                "xAxis": {
                    "type": "category",
                    "data": [
                        "2022-08-21",
                        "2022-08-22",
                        "2022-08-23",
                        "2022-08-24",
                        "2022-08-25",
                        "2022-08-26",
                        "2022-08-27",
                        "2022-08-28",
                        "2022-08-29",
                        "2022-08-30",
                        "2022-08-31",
                        "2022-09-01",
                        "2022-09-02",
                        "2022-09-03",
                        "2022-09-04",
                        "2022-09-05",
                        "2022-09-06",
                        "2022-09-07",
                        "2022-09-08",
                        "2022-09-09",
                        "2022-09-10",
                        "2022-09-11",
                        "2022-09-12",
                        "2022-09-13",
                        "2022-09-14",
                        "2022-09-15",
                        "2022-09-16",
                        "2022-09-17",
                        "2022-09-18",
                        "2022-09-19"
                    ]
                },
                "yAxis": {
                    "type": "value"
                },
                "legend": {},
                "series": [
                    {
                        "data": [
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0,
                            0
                        ],
                        "type": "line",
                        "name": "30天"
                    }
                ],
                "title": {
                    "text": "用户登录人数变化图",
                    "subtext": "过去30天"
                }
            }
        ]
    }

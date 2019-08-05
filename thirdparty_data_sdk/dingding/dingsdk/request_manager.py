"""
Manage request get, post and raise exception when api call failed
"""

import requests
from thirdparty_data_sdk.dingding.dingsdk.error_utils import APICallError


class RequestManager:
    """
    Manage request get, post and raise exception when api call failed
    """

    def __init__(self):
        self.request_count = 0

    def get(self, request_url=None, request_params=None):
        """
        处理Get请求
        :param request_url: 请求的链接
        :param request_params: 请求的参数
        :return:
        """

        self.request_count += 1

        res = requests.get(url=request_url, params=request_params)

        tmp_json = res.json()
        if tmp_json['errcode'] != 0:
            raise APICallError('errcode:%d, errmsg:%s.' % (tmp_json['errcode'],
                                                           tmp_json['errmsg']))

        return tmp_json

    def post(self, request_url=None, request_params=None, request_data=None):
        """
        处理post请求
        :param request_url: 请求链接
        :param request_params: 请求参数
        :param request_data: post的json数据结构
        :return:
        """

        self.request_count += 1

        res = requests.post(
            url=request_url,
            params=request_params,
            json=request_data,
        )

        tmp_json = res.json()
        if tmp_json['errcode'] != 0:
            raise APICallError('errcode:%d, errmsg:%s.' % (tmp_json['errcode'],
                                                           tmp_json['errmsg']))

        return tmp_json

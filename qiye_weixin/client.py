#!/usr/bin/env python3
import requests
import time
import json
import os
from common.logger import logger


class WeixinClient:
    def __init__(self, corpid, corpsecret, agentid, access_token=None):
        """
        配置初始信息
        """
        self.CORPID = corpid  # 企业ID
        self.CORPSECRET = corpsecret  # 应用Secret
        self.AGENTID = agentid  # 应用Agentid
        self.ACCESS_TOKEN = access_token  #

    def get_access_token(self):
        """
        调用接口返回登录信息access_token
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={self.CORPID}&corpsecret={self.CORPSECRET}"
        res = requests.get(url=url)
        return json.loads(res.text)['access_token']

    def send_textcard(self, touser, title, description, more_url, btntxt):
        """
        发送卡片文本消息
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.ACCESS_TOKEN}"
        send_values = {
            "touser": touser,
            "msgtype": "textcard",
            "agentid": self.AGENTID,
            "textcard": {
                "title": title,
                "description": description,
                "url": more_url,
                "btntxt": btntxt,
            },
        }
        body = bytes(json.dumps(send_values), 'utf-8')
        res = requests.post(url, body)
        logger.info(res.json())
        return res.json()['errmsg']

    def _upload_file(self, file):
        """
        先将文件上传到临时媒体库
        """
        url = f"https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={self.ACCESS_TOKEN()}&type=file"
        data = {"file": open(file, "rb")}
        res = requests.post(url, files=data)
        return res.json()['media_id']

    def send_file(self, file):
        """
        发送文件
        """
        media_id = self._upload_file(file)  # 先将文件上传至临时媒体库
        url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={self.ACCESS_TOKEN}"
        send_values = {
            "touser": self.TOUSER,
            "msgtype": "file",
            "agentid": self.AGENTID,
            "file": {"media_id": media_id},
        }
        send_message = bytes(json.dumps(send_values), 'utf-8')
        res = requests.post(url, send_message)
        return res.json()['errmsg']

    def upload_picture(self, file):
        """
        返回的url永久有效, 每个企业每天之多上传100张图片
        """
        url = f'https://qyapi.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self.ACCESS_TOKEN}'
        data = {"file": open(file, "rb")}
        res = requests.post(url, files=data)
        res = res.json()
        if res['errcode'] == 0:
            logger.info(res['url'])
            return res['url']
        else:
            logger.error(res['errmsg'])
            return None

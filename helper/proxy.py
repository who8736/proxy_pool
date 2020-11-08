# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Proxy
   Description :   代理对象类型封装
   Author :        JHao
   date：          2019/7/11
-------------------------------------------------
   Change Activity:
                   2019/7/11: 代理对象类型封装
-------------------------------------------------
"""
__author__ = 'JHao'

import json
from urllib.parse import urlparse
from setting import PROXY_SCORE_INIT


class Proxy(object):

    def __init__(self, url, score=PROXY_SCORE_INIT,
                 proxy_type='', tag='',
                 source=''):
        self._url = url
        self._score = score
        self._proxy_type = proxy_type
        self._tag = tag
        self._source = source

    @classmethod
    def createFromJson(cls, proxy_json):
        """
        根据proxy属性json创建Proxy实例
        :param proxy_json:
        :return:
        """
        proxy_dict = json.loads(proxy_json)
        return cls(url=proxy_dict.get("url", ""),
                   score=proxy_dict.get("score", PROXY_SCORE_INIT),
                   proxy_type=proxy_dict.get("proxy_type", ""),
                   tag=proxy_dict.get("tag", ""),
                   )

    # @property
    # def str(self):
    #     """ 代理 ip:port """
    #     return f'{self.protocol}://{self._ip}:{self.port}'

    @property
    def url(self):
        """ 代理地址，socks5://127.0.0.1:443 """
        return self._url

    @property
    def score(self):
        """ 协议 http/https/socks/socks5 """
        return self._score

    @property
    def proxy_type(self):
        """ 透明/匿名/高匿 """
        return self._proxy_type

    @property
    def tag(self):
        """ tag """
        return self._tag

    @property
    def to_dict(self):
        """ 属性字典 """
        return {"url": self._url,
                "score": self._score,
                "proxy_type": self._proxy_type,
                "tag": self._tag,
                }

    @property
    def to_json(self):
        """ 属性json格式 """
        return json.dumps(self.to_dict, ensure_ascii=False)

    # --- proxy method ---
    @url.setter
    def url(self, value):
        self._url = value

    @score.setter
    def score(self, value):
        self._score = value

    @proxy_type.setter
    def proxy_type(self, value):
        self._proxy_type = value

    @tag.setter
    def tag(self, value):
        self._tag = value


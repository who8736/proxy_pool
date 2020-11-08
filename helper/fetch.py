# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetchScheduler
   Description :
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06:
-------------------------------------------------
"""
__author__ = 'JHao'

from copy import deepcopy
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from fetcher.proxyFetcher import ProxyFetcher
from handler.configHandler import ConfigHandler
from setting import VERIFY_URL, PROXY_SCORE_INIT
from helper.proxy import Proxy


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()
        self.proxy_handler = ProxyHandler()

    def fetch(self):
        """
        fetch proxy into db with proxyFetcher
        :return:
        """
        proxy_set = set()
        url_set= set()
        self.log.info("ProxyFetch : start")
        for fetch_name in self.conf.fetchers:
            self.log.info("ProxyFetch - {func}: start".format(func=fetch_name))
            fetcher = getattr(ProxyFetcher, fetch_name, None)
            if not fetcher:
                self.log.error("ProxyFetch - {func}: class method not exists!")
                continue
            if not callable(fetcher):
                self.log.error("ProxyFetch - {func}: must be class method")
                continue

            try:
                for proxy in fetcher():
                    if proxy.url in url_set:
                        self.log.info(
                            f'ProxyFetch - {fetch_name}: {proxy.url} exist')
                        continue
                    self.log.info(f'ProxyFetch - {fetch_name}: {p.url} success')
                    for tag in VERIFY_URL.keys():
                        p = deepcopy(proxy)
                        p.tag = tag
                        proxy_set.add(p)
            except Exception as e:
                self.log.error("ProxyFetch - {func}: error".format(func=fetch_name))
                self.log.error(str(e))
        self.log.info("ProxyFetch - all complete!")
        return proxy_set


def runFetcher():
    return Fetcher().fetch()

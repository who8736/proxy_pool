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
                for url in fetcher():
                    for tag in VERIFY_URL.keys():
                        proxy = Proxy(url, tag=tag)
                        if proxy in proxy_set:
                            self.log.info(f'ProxyFetch - {fetch_name}: {proxy.url}->{proxy.tag} exist')
                            continue
                        else:
                            self.log.info(f'ProxyFetch - {fetch_name}: {proxy.url}->{proxy.tag} success')
                            # self.log.info('ProxyFetch - %s: %s success' % (fetch_name, proxy.ljust(23)))
                            proxy_set.add(proxy)
            except Exception as e:
                self.log.error("ProxyFetch - {func}: error".format(func=fetch_name))
                self.log.error(str(e))
        self.log.info("ProxyFetch - all complete!")
        return proxy_set


def runFetcher():
    return Fetcher().fetch()

# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06:
-------------------------------------------------
"""
__author__ = 'JHao'

from util.six import Empty
from threading import Thread
from datetime import datetime

from helper.proxy import Proxy
from util.validators import validators
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler
from db.sqlClient import SqlClient
from setting import (PROXY_SCORE_INIT, PROXY_SCORE_MAX, PROXY_SCORE_MIN,
                     PROXY_SCORE_PER,
                     THREADCNT,
                     )


def proxyCheck(proxy):
    """
    检测代理是否可用
    :param proxy: Proxy object
    :return: Proxy object, status
    """
    for func in validators:
        if not func(proxy):
            return False
    return True


class Checker(Thread):
    """
    多线程检测代理是否可用
    """

    def __init__(self, check_type, queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.type = check_type
        self.log = LogHandler("checker")
        # self.proxy_handler = ProxyHandler()
        self.queue = queue
        # self.conf = ConfigHandler()
        self.db = SqlClient()

    def run(self):
        self.log.info(f"ProxyCheck - {self.name}  : start")
        while True:
            try:
                proxy = self.queue.get(block=False)
            except Empty:
                self.log.info(f"ProxyCheck - {self.name}  : complete")
                break

            result = proxyCheck(proxy)
            loghead = f'ProxyCheck - {self.name}  : {proxy.url}->{proxy.tag} '
            if self.type == "raw":
                if result:
                    if self.db.exists(proxy):
                        self.log.info(f'{loghead} exists')
                    else:
                        self.log.info(f'{loghead} success')
                        self.db.put(proxy)
                else:
                    self.log.info(f'{loghead} fail')
            else:
                if result:
                    self.log.info(f'{loghead} pass, increase score')
                    self.db.increase(proxy, PROXY_SCORE_PER)
                else:
                    self.log.info(f'{loghead} fail, decrease score')
                    self.db.decrease(proxy, PROXY_SCORE_PER)
            self.queue.task_done()


def runChecker(tp, queue):
    """
    run Checker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(THREADCNT):
        thread_list.append(Checker(tp, queue, f"thread_{index:02}"))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

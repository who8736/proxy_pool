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


def proxyCheck(proxy):
    """
    检测代理是否可用
    :param proxy: Proxy object
    :return: Proxy object, status
    """

    def __proxyCheck(_proxy):
        for func in validators:
            if not func(_proxy):
                return False
        return True

    if __proxyCheck(proxy):
        # 检测通过 更新proxy属性
        proxy.last_status = 1
        if proxy.fail_count > 0:
            proxy.fail_count -= 1
    else:
        proxy.last_status = 0
        proxy.fail_count += 1
    proxy.check_count += 1
    proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return proxy


class Checker(Thread):
    """
    多线程检测代理是否可用
    """

    def __init__(self, check_type, queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.type = check_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.queue = queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info(f"ProxyCheck - {self.name}  : start")
        while True:
            try:
                proxy_json = self.queue.get(block=False)
            except Empty:
                self.log.info(f"ProxyCheck - {self.name}  : complete")
                break

            proxy = Proxy.createFromJson(proxy_json)
            proxy = proxyCheck(proxy)
            loghead = f'ProxyCheck - {self.name}  : {proxy.str} '
            if self.type == "raw":
                if proxy.last_status:
                    if self.proxy_handler.exists(proxy):
                        self.log.info(f'{loghead} exists')
                    else:
                        self.log.info(f'{loghead} success')
                        self.proxy_handler.put(proxy)
                else:
                    self.log.info(f'{loghead} fail')
            else:
                if proxy.last_status:
                    self.log.info(f'{loghead} pass')
                    self.proxy_handler.put(proxy)
                else:
                    if proxy.fail_count > self.conf.maxFailCount:
                        self.log.info(f'{loghead} fail, '
                                      f'count {proxy.fail_count} delete')
                        self.proxy_handler.delete(proxy)
                    else:
                        self.log.info(f'{loghead} fail, '
                                      f'count {proxy.fail_count} keep')
                        self.proxy_handler.put(proxy)
            self.queue.task_done()


def runChecker(tp, queue):
    """
    run Checker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(20):
        thread_list.append(Checker(tp, queue, f"thread_{index:02}"))

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

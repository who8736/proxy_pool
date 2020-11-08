# -*- coding:utf-8 -*-
# author:who8736
# datetime:2020/11/3 23:02

from helper.proxy import Proxy
from util.validators import formatValidator
from queue import Queue
from helper.fetch import runFetcher
from helper.check import Checker
from db.sqlClient import SqlClient

def testMain():
    proxy_queue = Queue()
    for proxy in runFetcher():
        proxy_queue.put(proxy)

    # runChecker("raw", proxy_queue)
    checker = Checker('raw', proxy_queue, f"thread_01")
    checker.start()
    checker.join()


def testExist():
    client = SqlClient()
    sql = 'select url from proxy where tag="b47w"'
    urls = [i[0] for i in client.engine.execute(sql).fetchall()]
    print(urls)
    proxy_queue = Queue()
    for url in urls:
        proxy = Proxy(url)
        proxy.tag = 'b47w'
        proxy_queue.put(proxy)
    checker = Checker('raw', proxy_queue, f"thread_01")
    checker.start()
    checker.join()


if __name__ == '__main__':
    pass
    # proxy = Proxy('socks5://49.89.87.151:9999', tag='b47w')
    # flag = formatValidator(proxy)
    # print(flag)
    testExist()

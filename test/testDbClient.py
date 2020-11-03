# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     testDbClient
   Description :
   Author :        JHao
   date：          2020/6/23
-------------------------------------------------
   Change Activity:
                   2020/6/23:
-------------------------------------------------
"""
__author__ = 'JHao'

from db.dbClient import DbClient
from db.sqlClient import SqlClient
from helper.proxy import Proxy

def testDbClient():
    #  ############### ssdb ###############
    ssdb_uri = "ssdb://:password@127.0.0.1:8888"
    s = DbClient.parseDbConn(ssdb_uri)
    assert s.db_type == "SSDB"
    assert s.db_pwd == "password"
    assert s.db_host == "127.0.0.1"
    assert s.db_port == 8888

    #  ############### redis ###############
    redis_uri = "redis://:password@127.0.0.1:6379/1"
    r = DbClient.parseDbConn(redis_uri)
    assert r.db_type == "REDIS"
    assert r.db_pwd == "password"
    assert r.db_host == "127.0.0.1"
    assert r.db_port == 6379
    assert r.db_name == "1"
    print("DbClient ok!")


def testMysqlClient():
    db = SqlClient()
    proxy = Proxy('socks://127.0.0.1:1000', tag='test')

    # 增加
    # db.put(proxy)

    # 取一个
    # geted = db.get()
    # print(geted)

    # 删除
    db.delete(proxy)


if __name__ == '__main__':
    pass

    # testDbClient()

    testMysqlClient()

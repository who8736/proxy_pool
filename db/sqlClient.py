# -*- coding: utf-8 -*-
'''
Created on 2016年11月21日

@author: who8736
'''
import os
import configparser
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import pandas as pd
# from initlog import initlog
# import config
from setting import (PROXY_SCORE_MIN, PROXY_SCORE_MAX, PROXY_SCORE_INIT,
                     SQLHOST, SQLUSER, SQLPASSWORD, SQLSCHEMA,
                     PROXY_SCORE_PER, PROXY_SCORE_SELECT)
from helper.proxy import Proxy


class SqlClient():
    """
    mysql client

    """

    def __init__(self, **kwargs):
        """
        init
        :param host: host
        :param port: port
        :param password: password
        :param db: db
        :return:
        """
        connectStr = (f'mysql://{SQLUSER}:{SQLPASSWORD}@{SQLHOST}'
                      f'/{SQLSCHEMA}?charset=utf8')
        self.engine = create_engine(connectStr,
                                    strategy='threadlocal', echo=False)

    def get(self, tag):
        """
        返回一个代理
        :return:
        """
        sql = (f'select url, score, proxy_type, tag from proxy '
               f'where score>={PROXY_SCORE_SELECT} and tag="{tag}"')
        print(sql)
        result = pd.read_sql(sql, self.engine)
        if not result.empty:
            proxy = result.sample(n=1)
            return proxy
        else:
            return None

    def put(self, proxy):
        """
        将代理放入hash, 使用changeTable指定hash name
        :param proxy: Proxy obj
        :return:
        """
        sql = (f'insert into proxy (url, score, proxy_type, tag, source) '
               f'values("{proxy.url}", "{proxy.score}", '
               f'"{proxy.proxy_type}", "{proxy.tag}", '
               f'"{proxy.souce}")')
        self.engine.execute(sql)

    # def pop(self):
    #     """
    #     弹出一个代理
    #     :return: dict {proxy: value}
    #     """
    #     proxies = self.__conn.hkeys(self.name)
    #     for proxy in proxies:
    #         proxy_info = self.__conn.hget(self.name, proxy)
    #         self.__conn.hdel(self.name, proxy)
    #         return proxy_info
    #     else:
    #         return False

    def delete(self, proxy):
        """
        移除指定代理, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        sql = f'delete from proxy where url="{proxy.url}" and tag="{proxy.tag}"'
        self.engine.execute(sql)

    def exists(self, proxy):
        """
        判断指定代理是否存在, 使用changeTable指定hash name
        :param proxy_str: proxy str
        :return:
        """
        sql = (f'select url from proxy '
               f'where url="{proxy.url}" and tag="{proxy.tag}"')
        df = pd.read_sql(sql, self.engine)
        return not df.empty

    # def update(self, proxy_obj):
    #     """
    #     更新 proxy 属性
    #     :param proxy_obj:
    #     :return:
    #     """
    #     return self.__conn.hset(self.name, proxy_obj.proxy, proxy_obj.to_json)

    def getAll(self, tag=None):
        """
        字典形式返回所有代理, 使用changeTable指定hash name
        :return:
        """
        sql = 'select url, score, proxy_type, tag from proxy'
        if tag is not None:
            sql += f' where tag="{tag}"'
        df = pd.read_sql(sql, self.engine)
        proxies = []
        for index, row in df.iterrows():
            proxy = Proxy.createFromJson(row.to_json())
            proxies.append(proxy)
        return proxies

    # def clear(self):
    #     """
    #     清空所有代理, 使用changeTable指定hash name
    #     :return:
    #     """
    #     return self.__conn.delete(self.name)

    def getCount(self, tag=None):
        """
        返回代理数量
        :return:
        """
        sql = 'select count(1) from proxy '
        if tag is not None:
            sql += f'where tag="{tag}"'
        return self.engine.execute(sql).fetchone()

    def increase(self, proxy, value):
        """
        加分
        :return:
        """
        score = self.getScore(proxy)
        if score is None:
            return None
        score += value
        if score > PROXY_SCORE_MAX:
            score = PROXY_SCORE_MAX
        self.setScore(proxy, score)

    def decrease(self, proxy, value):
        """
        减分
        :return:
        """
        score = self.getScore(proxy)
        if score is None:
            return None
        score -= value
        if score <= 0:
            self.delete(proxy)
        else:
            self.setScore(proxy, score)

    def getScore(self, proxy):
        sql = (f'select score from proxy '
               f'where url="{proxy.url}" and tag="{proxy.tag}"')
        score = self.engine.execute(sql)
        if score:
            return score.fetchone()
        else:
            return None

    def setScore(self, proxy, value):
        sql = (f'update proxy set score={value} '
               f'where url="{proxy.url}" and tag="{proxy.tag}"')
        self.engine.execute(sql)

    # def changeTable(self, name):
    #     """
    #     切换操作对象
    #     :param name:
    #     :return:
    #     """
    #     self.name = name

#     """建立mysql连接"""
#     def __init__(self, parent=None):
#         self.loadSQLConf()
#         connectStr = (f'mysql://{self.user}:{self.password}@{self.ip}'
#                       f'/avgirl?charset=utf8')
#         self.engine = create_engine(connectStr,
#                                     strategy='threadlocal', echo=False)
#         self.Session = scoped_session(
#             sessionmaker(bind=self.engine, autoflush=False))
#
#     def loadSQLConf(self):
#         mycnf = config.Config()
#         self.user = mycnf.sqlUser
#         self.password = mycnf.sqlPassword
#         self.ip = mycnf.sqlIp
#         # self.token = mycnf.tusharetoken
#
#
# sqlconn = SQLConn()
# engine = sqlconn.engine
# Session = sqlconn.Session
#

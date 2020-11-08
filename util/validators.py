# -*- coding: utf-8 -*-

import requests
import random
import re
from re import findall
from urllib.parse import urlparse
from handler.configHandler import ConfigHandler
from handler.logHandler import LogHandler
from helper.proxy import Proxy
from setting import VERIFY_URL
from util.webRequest import WebRequest

conf = ConfigHandler()
validators = []

logger = LogHandler("validators")


def validator(func):
    validators.append(func)
    return func


@validator
def formatValidator(proxy):
    """
    检查代理格式
    :param proxy:
    :return:
    """
    return True
    # try:
    #     protocols = ['HTTP', 'HTTPS', 'SOCKS4', 'SOCKS5']
    #     parsed = urlparse(proxy.url)
    #     flag = parsed.scheme.upper() in protocols
    #     ip_regex = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    #     _ip = findall(ip_regex, parsed.hostname)
    #     flag = flag and (len(_ip) == 1 and _ip[0] == parsed.hostname)
    #     port_regex = r"\d{1,5}"
    #     _port = findall(port_regex, str(parsed.port))
    #     flag = flag and (len(_port) == 1 and _port[0] == parsed.port)
    #     return flag
    # except Exception as e:
    #     logger.warning(f'{proxy.url}--{e}')


@validator
def timeOutValidator(proxy):
    """
    检测超时
    :param proxy:
    :return:
    """
    proxies = {"http": proxy.url, "https": proxy.url}
    try:
        r = WebRequest().get(VERIFY_URL[proxy.tag][0], proxies=proxies)
        verifyFlag = re.search(VERIFY_URL[proxy.tag][1], r.text)

        if r.response.status_code == 200 and verifyFlag:
            return True
    except Exception as e:
        pass
    return False


@validator
def customValidator(proxy):
    """
    自定义validator函数，校验代理是否可用
    :param proxy:
    :return:
    """

    return True

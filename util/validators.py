# -*- coding: utf-8 -*-

import requests
import random
from re import findall
from urllib.parse import urlparse
from handler.configHandler import ConfigHandler
from handler.logHandler import LogHandler
from helper.proxy import Proxy
from setting import UA, VERIFY_URL

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
    # if proxy_type in ('socks', 'socks5'):
    #     # proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    #     proxies = {'http': f'socks5h://{proxy}', 'https': f'socks5h://{proxy}'}
    # else:
    #     proxies = {'http': f'http://{proxy}', 'https': f'https://{proxy}'}
    #     # proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    headers = {'User-Agent': random.choice(UA),
               'Accept': '*/*',
               'Connection': 'keep-alive',
               'Accept-Language': 'zh-CN,zh;q=0.9'}
    try:
        r = requests.head(VERIFY_URL[proxy.tag],
                          headers=headers,
                          proxies=proxies,
                          timeout=conf.verifyTimeout,
                          verify=False)
        if r.status_code == 200:
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

# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from time import sleep
import requests
from lxml import etree
import base64
from random import choice
from urllib.parse import unquote, urlparse

from util.webRequest import WebRequest
from helper.proxy import Proxy
from setting import VERIFY_URL, PROXY_SCORE_INIT, MAINPROXY


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        :return:
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        key = 'ABCDEFGHIZ'
        for url in url_list:
            html_tree = WebRequest().get(url).tree
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    ip = ul.xpath('./span[1]/li/text()')[0]
                    classnames = ul.xpath('./span[2]/li/attribute::class')[0]
                    classname = classnames.split(' ')[1]
                    protocol = ul.xpath('./span[4]/li/text()')[0]
                    port_sum = 0
                    for c in classname:
                        port_sum *= 10
                        port_sum += key.index(c)
                    port = port_sum >> 3
                    yield f'{protocol}://{ip}:{port}'
                except Exception as e:
                    print(e)

    @staticmethod
    def freeProxy02(count=20):
        """
        代理66 http://www.66ip.cn/
        :param count: 提取数量
        :return:
        """
        urls = [
            "http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=",
            "http://www.66ip.cn/nmtq.php?getnum={}&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip"
        ]

        try:
            import execjs
            import requests

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                'Accept': '*/*',
                'Connection': 'keep-alive',
                'Accept-Language': 'zh-CN,zh;q=0.8'}
            session = requests.session()
            src = session.get("http://www.66ip.cn/", headers=headers).text
            src = src.split("</script>")[0] + '}'
            src = src.replace("<script>", "function test() {")
            src = src.replace("while(z++)try{eval(",
                              ';var num=10;while(z++)try{var tmp=')
            src = src.replace(");break}",
                              ";num--;if(tmp.search('cookie') != -1 | num<0){return tmp}}")
            ctx = execjs.compile(src)
            src = ctx.call("test")
            src = src[src.find("document.cookie="): src.find("};if((")]
            src = src.replace("document.cookie=", "")
            src = "function test() {var window={}; return %s }" % src
            cookie = execjs.compile(src).call('test')
            js_cookie = cookie.split(";")[0].split("=")[-1]
        except Exception as e:
            print(e)
            return

        for url in urls:
            try:
                html = session.get(url.format(count),
                                   cookies={"__jsl_clearance": js_cookie},
                                   headers=headers).text
                ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}",
                                 html)
                for ip in ips:
                    yield ip.strip()
            except Exception as e:
                print(e)
                pass

    @staticmethod
    def freeProxy03(page_count=1):
        """
        西刺代理 http://www.xicidaili.com
        :return:
        """
        url_list = [
            'http://www.xicidaili.com/nn/',  # 高匿
            'http://www.xicidaili.com/nt/',  # 透明
        ]
        for each_url in url_list:
            for i in range(1, page_count + 1):
                page_url = each_url + str(i)
                tree = WebRequest().get(page_url).tree
                proxy_list = tree.xpath(
                    './/table[@id="ip_list"]//tr[position()>1]')
                for proxy in proxy_list:
                    try:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass

    @staticmethod
    def freeProxy04():
        """
        guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = WebRequest().get(url).tree
        proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))

                # HTML中的port是随机数，真正的端口编码在class后面的字母中。
                # 比如这个：
                # <span class="port CFACE">9054</span>
                # CFACE解码后对应的是3128。
                port = 0
                for _ in each_proxy.xpath(".//span[contains(@class, 'port')]"
                                          "/attribute::class")[0]. \
                        replace("port ", ""):
                    port *= 10
                    port += (ord(_) - ord('A'))
                port /= 8

                yield '{}:{}'.format(ip_addr, int(port))
            except Exception as e:
                pass

    @staticmethod
    def freeProxy05(page_count=1):
        """
        快代理 https://www.kuaidaili.com
        """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """
        码农代理 https://proxy.coderbusy.com/
        :return:
        """
        urls = ['https://proxy.coderbusy.com/']
        for url in urls:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                try:
                    yield ('http://' + tr.xpath('./td[1]/text()')[0]
                           + ':' + tr.xpath('./td[2]/a/text()')[0])
                except IndexError:
                    continue

    @staticmethod
    def freeProxy07():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        urls = ['http://www.ip3366.net/free/?stype=1',
                "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>',
                r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """
        IP海 http://www.iphai.com/free/ng
        :return:
        """
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """
        http://ip.jiangxianli.com/?page=
        免费代理库
        :return:
        """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    # @staticmethod
    # def freeProxy10():
    #     """
    #     墙外网站 cn-proxy
    #     :return:
    #     """
    #     urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    # @staticmethod
    # def freeProxy11():
    #     """
    #     https://proxy-list.org/english/index.php
    #     :return:
    #     """
    #     urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
    #     request = WebRequest()
    #     import base64
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
    #         for proxy in proxies:
    #             yield base64.b64decode(proxy).decode()

    # @staticmethod
    # def freeProxy12():
    #     urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    @staticmethod
    def freeProxy13(max_page=2):
        """
        http://www.qydaili.com/free/?action=china&page=1
        齐云代理
        :param max_page:
        :return:
        """
        base_url = 'http://www.qydaili.com/free/?action=china&page='
        for page in range(1, max_page + 1):
            url = base_url + str(page)
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td.*?>(\d+)</td>',
                r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxy14(max_page=2):
        """
        http://www.89ip.cn/index.html
        89免费代理
        :param max_page:
        :return:
        """
        base_url = 'http://www.89ip.cn/index_{}.html'
        for page in range(1, max_page + 1):
            url = base_url.format(page)
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(
                r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
                r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxy15():
        urls = ['http://www.xiladaili.com/putong/',
                "http://www.xiladaili.com/gaoni/",
                "http://www.xiladaili.com/http/",
                "http://www.xiladaili.com/https/"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}",
                             r.text)
            for ip in ips:
                yield ip.strip()

    @staticmethod
    def freeProxy16():
        proxies = {'http': MAINPROXY, 'https': MAINPROXY}
        source = 'free-proxy.cz'
        urls = [
            'http://free-proxy.cz/en/proxylist/country/all/socks5/ping/all',
            'http://free-proxy.cz/en/proxylist/country/all/socks5/ping/all/2',
            'http://free-proxy.cz/en/proxylist/country/all/socks5/ping/all/3',
            'http://free-proxy.cz/en/proxylist/country/all/socks5/ping/all/4',
            'http://free-proxy.cz/en/proxylist/country/all/socks5/ping/all/5',
        ]
        for url in urls:
            r = WebRequest().get(url, proxies=proxies)
            if r.response.status_code == 200:
                ret = r.tree
                for tr in ret.xpath('//table[@id="proxy_list"]//tr')[1:]:
                    try:
                        ip_script = tr.xpath('./td[1]/script/text()')[0]
                        ip_base64 = re.search('(?:")([\w=]+)(?:")',
                                              ip_script).groups()[0]
                        ip = base64.b64decode(ip_base64).decode('utf8')
                        port = tr.xpath('./td[2]/span/text()')[0]
                        protocol = ''.join(tr.xpath('./td[3]/small/text()'))
                        yield Proxy(f'{protocol}://{ip}:{port}',
                                    source=source)
                    except Exception as e:
                        print(e)

    @staticmethod
    def freeProxy17():
        source = 'www.proxynova.com'
        urls = [
            'https://www.proxynova.com/proxy-server-list/elite-proxies/',
        ]
        proxies = {'http': MAINPROXY, 'https': MAINPROXY}
        for url in urls:
            tree = WebRequest().get(url, proxies=proxies).tree
            if tree is None:
                return None
            ret = tree.xpath('//*[@id="tbl_proxy_list"]/tbody/tr')
            for r in ret:
                try:
                    ip_script = r.xpath('./td[1]/abbr/script/text()')[0]
                    ip = re.search('(?:\')(.+)(?:\')',
                                          ip_script).groups()[0]
                    port = r.xpath('./td[2]/text()')[0].strip()
                    protocol = 'https'
                    yield Proxy(f'{protocol}://{ip}:{port}',
                                source=source)
                except Exception as e:
                    print(e)

    @staticmethod
    def freeProxy18():
        source = 'spys.one'
        urls = [
            'https://spys.one/en/free-proxy-list/',
        ]
        proxies = {'http': MAINPROXY, 'https': MAINPROXY}
        for url in urls:
            tree = WebRequest().get(url, proxies=proxies).tree
            if tree is None:
                return None
            ret = tree.xpath('//*[@id="proxy_list"]/tbody/tr')
            for r in ret:
                try:
                    ip_script = r.xpath('./td[1]/script/text()')[0]
                    ip_base64 = re.search('(?:")([\w=]+)(?:")',
                                          ip_script).groups()[0]
                    ip = base64.b64decode(ip_base64).decode('utf8')
                    port = r.xpath('./td[2]/span/text()')[0]
                    protocol = r.xpath('./td[3]/small/text()')[0]
                    yield Proxy(f'{protocol}://{ip}:{port}',
                                source=source)
                except Exception as e:
                    print(e)

    @staticmethod
    def freeProxy19():
        source = 'www.freeproxylists.net'
        urls = [
            'http://www.freeproxylists.net/zh/?c=&pt=&pr=HTTPS&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50',
        ]
        proxies = {'http': MAINPROXY, 'https': MAINPROXY}
        for url in urls:
            tree = WebRequest().get(url, proxies=proxies).tree
            if tree is None:
                return None
            ret = tree.xpath('//tr')[4:]
            for r in ret:
                try:
                    ip_script = r.xpath('./td[1]/script/text()')[0]
                    ip_mask = re.search('(?:")(.*)(?:")',
                                          ip_script).groups()[0]
                    ip = re.search('(?:>)([0-9\.]+)(?:<)',
                                        unquote(ip_mask, 'utf8')).groups()[0]
                    port = r.xpath('./td[2]/text()')[0]
                    protocol = r.xpath('./td[3]/text()')[0]
                    yield Proxy(f'{protocol}://{ip}:{port}',
                                source=source)
                except Exception as e:
                    print(type(e), e)

    @staticmethod
    def freeProxy20():
        source = 'premproxy.com'
        urls = [
            'https://premproxy.com/list/ip-port/1.htm',
            'https://premproxy.com/list/ip-port/2.htm',
            'https://premproxy.com/list/ip-port/3.htm',
        ]
        proxies = {'http': MAINPROXY, 'https': MAINPROXY}
        for url in urls:
            tree = WebRequest().get(url, proxies=proxies).tree
            if tree is None:
                return None
            ret = tree.xpath('//ul[@id="ipportlist"]/li')
            for r in ret:
                try:
                    ip = r.xpath('./li/text()')[0][:-1]
                    # ip_mask = re.search('(?:")(.*)(?:")',
                    #                     ip_script).groups()[0]
                    # ip = re.search('(?:>)([0-9\.]+)(?:<)',
                    #                unquote(ip_mask, 'utf8')).groups()[0]
                    port = r.xpath('./li/span/text()')[0]
                    protocol = 'https'
                    yield Proxy(f'{protocol}://{ip}:{port}',
                                source=source)
                except Exception as e:
                    print(type(e), e)

    @staticmethod
    def freeProxy21():
        source = 'www.proxyranker.com'
        urls = [
            'https://www.proxyranker.com/china/list/',
            'https://www.proxyranker.com/china/list-2/',
            'https://www.proxyranker.com/china/list-3/',
            'https://www.proxyranker.com/china/list-4/',
        ]
        proxies = {'http': MAINPROXY, 'https': MAINPROXY}
        for url in urls:
            tree = WebRequest().get(url, proxies=proxies).tree
            if tree is None:
                return None
            ret = tree.xpath('//div[@class="bl"]//tr')[1:]
            for r in ret[:-1]:
                try:
                    ip = r.xpath('./td[1]/text()')[0]
                    port = r.xpath('./td[4]/span/text()')[0]
                    protocol = 'https'
                    yield Proxy(f'{protocol}://{ip}:{port}',
                                source=source)
                except Exception as e:
                    print(type(e), e)

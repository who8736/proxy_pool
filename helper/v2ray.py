import sys
import time
import requests
import socket
from base64 import b64decode, b64encode
import json
import copy
import os
from setting import (ROOT_PATH, V2RAYPATH, V2RAYVERIFYURL, V2RAYSUBSCRIPTION,
                     V2RAYSTARTPORT, V2RAYTHREADNUM)
import random
from threading import Thread
from queue import Queue
import subprocess

from util.webRequest import WebRequest


def getSub():
    """订阅节点"""
    nodes = []
    ips = set()
    for url in V2RAYSUBSCRIPTION:
        response = requests.get(url)
        # print(response.text.strip())
        # print(response.content)
        # print(type(response.text))
        nodesStr = b64decode(response.text).decode('utf8')
        # print(nodes)
        for nodebase64 in nodesStr.split('\n'):
            nodebase64 = nodebase64[8:]
            nodeStr = b64decode(nodebase64).decode('utf8')
            try:
                node = json.loads(nodeStr)
                if node['add'] not in ips:
                    nodes.append(node)
                    ips.add(node['add'])
            except Exception as e:
                print(f'nodeStr:{nodeStr}')
                print(e)
    return nodes
    # return nodes[:3]


def writeFile():
    nodes = getSub()
    filename = os.path.join(ROOT_PATH, 'nodes.json')
    with open(filename, 'w', encoding='utf8') as f:
        json.dump(nodes, f)


def readFile():
    nodes = None
    filename = os.path.join(ROOT_PATH, 'nodes.json')
    with open(filename, 'r', encoding='utf8') as f:
        nodes = json.load(f)
        for node in nodes:
            # print(node)
            yield node


def genV2rayConifg(node, inport, filename):
    samplefilename = os.path.join(ROOT_PATH, 'v2raysample.json')
    with open(samplefilename, 'r', encoding='utf8') as f:
        config = json.load(f)

    # 配置代理出口
    vnext = [{
        'address': node['add'],
        'port': int(node['port']),
        'users': [{
            'id': node['id'],
            'alterId': int(node['aid']),
            'email': 'f@f.ff',
            'security': 'auto',
            'encryption': None,
            'flow': None
        }]
    }]
    outbound = config['outbounds'][0]
    outbound['settings']['vnext'] = vnext
    outstream = outbound['streamSettings']
    outstream['network'] = node['net']
    outstream['security'] = node['tls']
    outstream['tlsSettings']['serverName'] = node['host']
    outstream['wsSettings']['path'] = node['path']
    outstream['wsSettings']['headers']['Host'] = node['host']
    outbound['streamSettings'] = outstream
    config['outbounds'][0] = outbound

    # 配置代理入口
    config['inbounds'][0]['port'] = inport

    # print(config)
    with open(filename, 'w', encoding='utf8') as f:
        # print('save file:', filename)
        json.dump(config, f)


def genV2rayConifgPlus(nodes, inport=52026):
    samplefilename = os.path.join(ROOT_PATH, 'v2raysample.json')
    with open(samplefilename, 'r', encoding='utf8') as f:
        config = json.load(f)

    outbase = copy.deepcopy(config['outbounds'][0])
    config['outbounds'].clear()
    proxyid = 0
    for node in nodes:
        outbound = copy.deepcopy(outbase)
        # 配置代理出口
        outbound['tag'] = f'proxy{proxyid:03}'
        proxyid += 1
        vnext = [{
            'address': node['add'],
            'port': int(node['port']),
            'users': [{
                'id': node['id'],
                'alterId': int(node['aid']),
                'email': 'f@f.ff',
                'security': 'auto',
                'encryption': None,
                'flow': None
            }]
        }]
        outbound['settings']['vnext'] = vnext
        outstream = outbound['streamSettings']
        outstream['network'] = node['net']
        outstream['security'] = node['tls']
        outstream['tlsSettings']['serverName'] = node['host']
        outstream['wsSettings']['path'] = node['path']
        outstream['wsSettings']['headers']['Host'] = node['host']
        outbound['streamSettings'] = outstream
        config['outbounds'].append(outbound)

    # 配置代理入口
    config['inbounds'][0]['port'] = inport

    # print(config)
    filename = os.path.join(V2RAYPATH, 'configplus.json')
    with open(filename, 'w', encoding='utf8') as f:
        # print('save file:', filename)
        json.dump(config, f)


def getV2rayPort(port=26520):
    while port_in_use(port):
        port += 1
    return port


def port_in_use(port):
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('127.0.0.1', port))
        return True
    except socket.error:
        return False
    finally:
        if s:
            s.close()


class V2rayClient(Thread):
    """以线程运行v2ray客户端"""

    def __init__(self, filename):
        Thread.__init__(self)
        self.filename = filename
        self.p = None

    def run(self):
        v2raycmd = os.path.join(V2RAYPATH, 'v2ray.exe')
        cmd = f'"{v2raycmd}" -config {self.filename}'
        print(cmd)
        # subprocess.run(cmd)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        self.p = subprocess.Popen([v2raycmd, '-config', self.filename],
                                  close_fds=True,
                                  shell=False,
                                  stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  startupinfo=startupinfo,
                                  # preexec_fn=os.setsid,
                                  )
        print('启动进程:', self.p.pid)

    def close(self):
        # p.kill() #无法杀掉所有子进程，只能杀掉子shell的进程

        # p.terminate()  #无法杀掉所有子进程
        print('结束进程:', self.p.pid)
        # os.killpg(self.p.pid, signal.SIGUSR1)
        # os.kill(self.p.pid, signal.CTRL_C_EVENT)
        # os.kill(self.p.pid, signal.CTRL_BREAK_EVENT)
        self.p.kill()


def v2rayChecker(inport):
    """验证v2ray节点

    """
    proxies = {
        'http': f'socks5://127.0.0.1:{inport}',
        'https': f'socks5://127.0.0.1:{inport}',
    }
    res = WebRequest().get(V2RAYVERIFYURL, proxies=proxies)
    print('response.status_code:', res.response.status_code)
    print('response.status_code type:', type(res.response.status_code))
    # print(res.response.text)
    return res.response.status_code == 200


class V2rayDaemon(Thread):
    """以线程运行v2ray客户端"""

    def __init__(self, threadId, nodeQueue, portQueue, okQueue):
        Thread.__init__(self)
        self.threadId = threadId
        self.nodeQueue = nodeQueue
        self.portQueue = portQueue
        self.okQueue = okQueue
        pass

    def run(self):
        while not self.nodeQueue.empty():
            node = self.nodeQueue.get()
            port = self.portQueue.get()
            filename = os.path.join(ROOT_PATH, 'tmp',
                                    f'config{self.threadId}.json')
            genV2rayConifg(node, port, filename)
            v2rayClient = V2rayClient(filename)
            v2rayClient.start()
            v2rayClient.join(timeout=2)
            flag = v2rayChecker(port)
            print(f'port:{port}', flag)
            if flag:
                self.okQueue.put(node)
            self.portQueue.put(port)
            # time.sleep(10)
            v2rayClient.close()


def v2rayMainChecker():
    nodeQueue = Queue()
    # for node in readFile():
    for node in getSub():
        nodeQueue.put(node)
    print('总节点数:', nodeQueue.qsize())

    portQueue = Queue()
    for port in range(V2RAYSTARTPORT, V2RAYSTARTPORT + V2RAYTHREADNUM):
        portQueue.put(port)

    okQueue = Queue()
    threads = []
    for tid in range(1, V2RAYTHREADNUM + 1):
        th = V2rayDaemon(tid, nodeQueue, portQueue, okQueue)
        # th.setDaemon(True)
        th.start()
        threads.append(th)

    for th in threads:
        th.join()

    print('成功节点数:', okQueue.qsize())
    okNodes = []
    while not okQueue.empty():
        node = okQueue.get()
        okNodes.append(node)
        print(node)

    return okNodes


if __name__ == '__main__':
    pass
    # writeFile()

    # a = list(readFile())[0]
    # print('-' * 80)
    # print(a)

    # 生成配置文件
    # filename = os.path.join(ROOT_PATH, 'tmp', 'config1.json')
    # print('save file:', filename)
    # node = list(readFile())[0]
    # genV2rayConifg(node, filename=filename, inport=26520)

    # url = 'ew0KICAidiI6ICIyIiwNCiAgInBzIjogImdpdGh1Yi5jb20vZnJlZWZxIC0g576O5Zu95YaF5Y2O6L6+5bee5ouJ5pav57u05Yqg5pavQnV5Vk0yMjkiLA0KICAiYWRkIjogIm1nYS5jZW50b3M4LmNsb3VkIiwNCiAgInBvcnQiOiAiNDQzIiwNCiAgImlkIjogIjliZjBiMmExLWY4OTAtM2Q3OS1iYTBiLTBhYTM1YTA0ZDhkNSIsDQogICJhaWQiOiAiMTYiLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIm1nYS5jZW50b3M4LmNsb3VkIiwNCiAgInBhdGgiOiAiL21vdmllIiwNCiAgInRscyI6ICJ0bHMiDQp9'
    # nodeStr = b64decode(url).decode('utf8')
    # node = json.loads(nodeStr)
    # print(node)

    # 获取空端口
    # port = 10801
    # while port <= 10820:
    #     # port = getV2rayPort(port)
    #     flag = check_port_in_use(port)
    #     print(port, flag)
    #     port += 1

    # 运行客户端
    # filename = os.path.join(ROOT_PATH, 'tmp', 'config1.json')
    # print(filename)
    # runClient(filename)

    # 检测节点并保存
    okNodes = v2rayMainChecker()
    with open(os.path.join(ROOT_PATH, 'tmp', 'oknodes.json'), 'w',
              encoding='utf8') as f:
        json.dump(okNodes, f)

    # 订阅节点
    # nodes = getSub()
    # for node in nodes:
    #     print(node)
    # print(f'总节点:{len(nodes)}')

    # 读取已检测节点并生成增强版配置
    with open(os.path.join(ROOT_PATH, 'tmp', 'oknodes.json'), 'r', encoding='utf8') as f:
        okNodes = json.load(f)
    genV2rayConifgPlus(okNodes)

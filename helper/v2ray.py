import sys
import requests
import socket
from base64 import b64decode, b64encode
import json
import os
from setting import ROOT_PATH, V2RAYPATH, V2RAYVERIFYURL
import random
from threading import Thread
from queue import Queue
import subprocess

from util.webRequest import WebRequest


def getSub():
    """订阅节点"""
    nodes = []
    for url in SUBSCRIPTION:
        response = requests.get(url)
        # print(response.text.strip())
        # print(response.content)
        # print(type(response.text))
        nodesStr = b64decode(response.text).decode('utf8')
        # print(nodes)
        for nodebase64 in nodesStr.split('\n'):
            nodebase64 = nodebase64[8:]
            nodeStr = b64decode(nodebase64).decode('utf8')
            node = json.loads(nodeStr)
            nodes.append(node)
    return nodes


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
        pass

    def run(self):
        v2raycmd = os.path.join(V2RAYPATH, 'v2ray.exe')
        cmd = f'"{v2raycmd}" -config {self.filename}'
        print(cmd)
        subprocess.run(cmd)


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
        node = self.nodeQueue.get()
        port = self.portQueue.get()
        filename = os.path.join(ROOT_PATH, 'tmp', f'config{self.threadId}.json')
        genV2rayConifg(node, port, filename)
        v2rayClient = V2rayClient(filename)
        v2rayClient.start()
        v2rayClient.join(timeout=3)
        flag = v2rayChecker(port)
        print(f'port:{port}', flag)
        if not flag:
            self.okQueue.put(node)
        self.portQueue.put(port)
        sys.exit(-1)


def v2rayMainThread():
    threadNum = 2
    startPort = 26520

    nodeQueue = Queue()
    # for node in readFile():
    for node in list(readFile())[:1]:
        nodeQueue.put(node)

    portQueue = Queue()
    for port in range(startPort, startPort + threadNum):
        portQueue.put(port)

    okQueue = Queue()
    while not nodeQueue.empty():
        th = V2rayDaemon(1, nodeQueue, portQueue, okQueue)
        # th.setDaemon(True)
        th.start()
        th.join()

    while not okQueue.empty():
        node = okQueue.get()
        print(node)

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

    v2rayMainThread()
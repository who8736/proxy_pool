import requests
import socket
from base64 import b64decode, b64encode
import json
import os
from setting import ROOT_PATH

SUBSCRIPTION = [
    'https://raw.fastgit.org/ntkernel/lantern/master/vmess_base64.txt',
]


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


def genV2rayConifg(node, filename, inport=1080):
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
        print('save file:', filename)
        json.dump(config, f)


def getV2rayPort(startPort=26000, stopPort=27000):
    sock = socket.socket()
    sock.bind(('', 0))
    ip, port = sock.getnameinfo()
    print(port)
    sock.close()
    return port


if __name__ == '__main__':
    pass
    # a = list(readFile())[0]
    # print('-' * 80)
    # print(a)

    # 生成配置文件
    # filename = os.path.join(ROOT_PATH, 'config1.json')
    # print('save file:', filename)
    # node = list(readFile())[0]
    # genV2rayConifg(node, filename=filename, inport=10803)

    # url = 'ew0KICAidiI6ICIyIiwNCiAgInBzIjogImdpdGh1Yi5jb20vZnJlZWZxIC0g576O5Zu95YaF5Y2O6L6+5bee5ouJ5pav57u05Yqg5pavQnV5Vk0yMjkiLA0KICAiYWRkIjogIm1nYS5jZW50b3M4LmNsb3VkIiwNCiAgInBvcnQiOiAiNDQzIiwNCiAgImlkIjogIjliZjBiMmExLWY4OTAtM2Q3OS1iYTBiLTBhYTM1YTA0ZDhkNSIsDQogICJhaWQiOiAiMTYiLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIm1nYS5jZW50b3M4LmNsb3VkIiwNCiAgInBhdGgiOiAiL21vdmllIiwNCiAgInRscyI6ICJ0bHMiDQp9'
    # nodeStr = b64decode(url).decode('utf8')
    # node = json.loads(nodeStr)
    # print(node)

    # 获取空端口
    getV2rayPort()


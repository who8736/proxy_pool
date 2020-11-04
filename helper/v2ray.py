import requests
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


def genV2rayConifg(outfilename, inport=1080):
    filename = os.path.join(ROOT_PATH, 'v2raysample.json')
    with open(filename, 'r', encoding='utf8') as f:
        config = json.load(f)

    node = list(readFile())[0]

    vnext = [{
        'address': node['add'],
        'port': int(node['port']),
        'users': [
            {
                'id': node['id'],
                'alterId': int(node['aid']),
                'email': 'f@f.ff',
                'security': 'auto',
                'encryption': None,
                'flow': None
            }
        ]
    }]
    config['outbounds'][0]['settings']['vnext'] = vnext
    config['outbounds'][0]['streamSettings']['network'] = node['net']
    config['outbounds'][0]['streamSettings']['security'] = node['tls']
    config['outbounds'][0]['streamSettings']['tlsSettings']['serverName'] = node[
        'host']
    config['outbounds'][0]['streamSettings']['wsSettings']['path'] = node['path']
    config['outbounds'][0]['streamSettings']['wsSettings']['headers']['Host'] = node['host']
    config['inbounds'][0]['port'] = inport
    # print(config)
    with open(outfilename, 'w', encoding='utf8') as f:
        print('save file:', outfilename)
        json.dump(config, f)


if __name__ == '__main__':
    pass
    # a = list(readFile())[0]
    # print('-' * 80)
    # print(a)

    filename = os.path.join(ROOT_PATH, 'config1.json')
    print('save file:', filename)
    genV2rayConifg(filename, inport=10803)

    # url = 'ew0KICAidiI6ICIyIiwNCiAgInBzIjogImdpdGh1Yi5jb20vZnJlZWZxIC0g576O5Zu95YaF5Y2O6L6+5bee5ouJ5pav57u05Yqg5pavQnV5Vk0yMjkiLA0KICAiYWRkIjogIm1nYS5jZW50b3M4LmNsb3VkIiwNCiAgInBvcnQiOiAiNDQzIiwNCiAgImlkIjogIjliZjBiMmExLWY4OTAtM2Q3OS1iYTBiLTBhYTM1YTA0ZDhkNSIsDQogICJhaWQiOiAiMTYiLA0KICAibmV0IjogIndzIiwNCiAgInR5cGUiOiAibm9uZSIsDQogICJob3N0IjogIm1nYS5jZW50b3M4LmNsb3VkIiwNCiAgInBhdGgiOiAiL21vdmllIiwNCiAgInRscyI6ICJ0bHMiDQp9'
    # nodeStr = b64decode(url).decode('utf8')
    # node = json.loads(nodeStr)
    # print(node)

    # a = {
    #     'v': '2',
    #     'ps': 'github.com/freefq - 美国内华达州拉斯维加斯BuyVM229',
    #     'add': 'mga.centos8.cloud',
    #     'port': '443',
    #     'id': '9bf0b2a1-f890-3d79-ba0b-0aa35a04d8d5',
    #     'aid': '16',
    #     'net': 'ws',
    #     'type': 'none',
    #     'host': 'mga.centos8.cloud',
    #     'path': '/movie',
    #     'tls': 'tls'
    # }

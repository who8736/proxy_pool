# -*- coding:utf-8 -*-
# author:who8736
# datetime:2020/11/3 23:02

from helper.proxy import Proxy
from util.validators import formatValidator

if __name__ == '__main__':
    proxy = Proxy('socks5://49.89.87.151:9999', tag='b47w')
    flag = formatValidator(proxy)
    print(flag)

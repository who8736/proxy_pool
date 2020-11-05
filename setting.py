# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
-------------------------------------------------
"""
import os

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.1.1"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010
MAINPROXY = 'socks5://127.0.0.1:10808'

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:@127.0.0.1:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'

# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "freeProxy16",

    "freeProxy01",
    # "freeProxy04",
    # "freeProxy05",
    # "freeProxy07",
    # "freeProxy09",
    # "freeProxy14",
    # "freeProxy15",

    # "freeProxy02",
    # "freeProxy03",
    # "freeProxy06",
    # "freeProxy08",
    # "freeProxy13",

]

# ############# proxy validator #################
VERIFY_URL = {
    'default': 'http://www.baidu.com',
    'b47w': 'http://www.b47w.com',
    # 'sukebei': 'https://sukebei.nyaa.si'
}
# VERIFY_URL = "https://sukebei.nyaa.si"

VERIFY_TIMEOUT = 10

MAX_FAIL_COUNT = 0

# 线程数量
THREADCNT = 20
# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and 
#   "ValueError: Timezone offset does not match system offset" 
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

# TIMEZONE = "Asia/Shanghai"
# CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
# ROOT_PATH = os.path.join(CURRENT_PATH, os.pardir)

# ############# log config #################
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(ROOT_PATH, 'log')
LOG_FORMAT = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'



# definition of proxy scores
PROXY_SCORE_MAX = 60
PROXY_SCORE_MIN = 0
PROXY_SCORE_INIT = 30
# 每次加减的分数
PROXY_SCORE_PER = 10
# 大于这个分数的才会被选中
PROXY_SCORE_SELECT = 10

# ############# v2ray config #################
V2RAYPATH = 'D:\\v2ray-windows-64'
V2RAYSUBSCRIPTION = [
    'https://raw.fastgit.org/ntkernel/lantern/master/vmess_base64.txt',
    'https://raw.fastgit.org/freefq/free/master/v2',
    'https://raw.fastgit.org/ssrsub/ssr/master/v2ray',
]
V2RAYVERIFYURL = 'https://www.google.com'
V2RAYTHREADNUM = 10
V2RAYSTARTPORT = 26520

# ############# mysql config #################
SQLHOST = '127.0.0.1'
SQLUSER = 'root'
SQLPASSWORD = 'root'
SQLSCHEMA = 'proxy'

# ############# private config #################
if os.path.isfile(os.path.join(ROOT_PATH, 'private', 'setting.py')):
    # print('import private')
    from private.setting import *
    # print(SQLPASSWORD)
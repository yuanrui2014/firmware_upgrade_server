#!/usr/bin/env python
# encoding: utf-8
'''
@author: Jerry Lee
@contact: liweizhong@nekteck.com
@software: Yuanrui
@file: funcs.py
@time: 2021/10/14 17:02
@desc:
'''

import socket


def get_local_ip():
    # 获取本机计算机名称
    hostname = socket.gethostname()

    # 获取本机ip
    ip = socket.gethostbyname(hostname)

    return ip
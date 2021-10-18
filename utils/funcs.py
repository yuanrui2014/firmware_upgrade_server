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

import xlrd


def get_local_ip():
    # 获取本机计算机名称
    hostname = socket.gethostname()

    # 获取本机ip
    ip = socket.gethostbyname(hostname)

    return ip


def read_xls_file(filename):
    """
    从excel文件中读取所有的mac地址
    :param filename:
    :return: testcase 列表
    """
    workbook = xlrd.open_workbook(filename)
    booksheet = workbook.sheet_by_index(0)  # 用索引取第一个sheet

    nrows = booksheet.nrows

    mac_addr_list = []
    for i in range(0, nrows):
        mac_addr = booksheet.cell_value(i, 0)
        mac_addr_list.append(mac_addr)

    return mac_addr_list

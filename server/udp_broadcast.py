#!/usr/bin/env python
# encoding: utf-8
'''
@author: Jerry Lee
@contact: liweizhong@nekteck.com
@software: Yuanrui
@file: udp_broadcast.py
@time: 2021/10/14 16:32
@desc:
'''

from socket import *
import time
from threading import Thread
from utils import logger
from utils.funcs import get_local_ip


class UdpBroadcast(Thread):
    def __init__(self, port):
        Thread.__init__(self)
        self.host = '<broadcast>'
        self.port = port
        self.buf_size = 1024

        self.addr = (self.host, self.port)

        self.stopped = False

    def run(self):
        self.stopped = False

        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind(('', 0))
        udp_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        ip_addr = get_local_ip()

        logger.info("get local ip: {}".format(ip_addr))

        while not self.stopped:
            data = ip_addr.encode("ascii")
            if not data:
                break
            #print("sending -> %s" % data)
            udp_socket.sendto(data, self.addr)

            time.sleep(1)  # 暂停1秒再广播

        udp_socket.close()

        logger.info("udp broadcast stopped")

    def shutdown(self):
        self.stopped = True
        self.join()

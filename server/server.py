#!/usr/bin/env python
# encoding: utf-8
'''
@author: Jerry Lee
@contact: liweizhong@nekteck.com
@software: Yuanrui
@file: server.py
@time: 2021/10/9 15:51
@desc:
'''

from threading import Thread
import webbrowser
import http.server
import socketserver
import time

http_server = None


def startServer(port):
    handler = http.server.SimpleHTTPRequestHandler

    global http_server
    http_server = socketserver.TCPServer(("", port), handler)

    print("Start server at port", port)
    http_server.serve_forever()


def start(port):
    thread = Thread(target=startServer, args=[port])
    thread.start()

    startTime = int(time.time())
    while not http_server:
        if int(time.time()) > startTime + 60:
            print("Time out")
            break
    return http_server


def stop():
    if http_server:
        http_server.shutdown()


def openUrl(port_number):
    url = "http://localhost:" + str(port_number)
    webbrowser.open(url)
    print(url + " is opened in browser")


# if __name__ == "__main__":
#     port_number = 8000
#     start(port_number)
#     openUrl(port_number)

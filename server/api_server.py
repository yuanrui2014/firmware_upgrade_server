#!/usr/bin/env python
# encoding: utf-8
'''
@author: Jerry Lee
@contact: liweizhong@nekteck.com
@software: Yuanrui
@file: api_server.py
@time: 2021/10/11 13:43
@desc:
'''
import os
from threading import Thread

from flask import Flask, make_response, send_from_directory, jsonify, request
from werkzeug.serving import make_server

from utils import logger, FIRMWARE_VERSION

server = None


class ServerThread(Thread):
    def __init__(self, app, port):
        Thread.__init__(self)
        self.srv = make_server('0.0.0.0', port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def start_server(port, client):
    global server
    app = Flask('firmware upgrade server')

    @app.route('/api/v1/upgrade/download/<filename>', methods=['GET'])
    def download(filename):
        exec_path = client.folder
        file_path = '/'.join([exec_path, filename])
        logger.info('download file {}'.format(file_path))
        if os.path.exists(file_path) and (filename == client.filename):
            mac = request.args.get('mac')

            client.callback_signal.emit({'type': 'download', 'content': {'mac': mac}})

            return make_response(send_from_directory(client.folder, filename, as_attachment=True))
        else:
            return '{}目录下没有找到名称为{}的文件'.format(exec_path, filename)

    @app.route('/api/v1/upgrade/connect', methods=['GET'])
    def connect():
        mac = request.args.get("mac")
        version = request.args.get("version")
        finish = request.args.get("finish")

        if finish is not None:
            client.callback_signal.emit({'type': 'finish', 'content': {'version': version, 'mac': mac, 'finish': int(finish)}})
        else:
            client.callback_signal.emit({'type': 'connect', 'content': {'version': version, 'mac': mac}})

        logger.info("{} connected, version: {}".format(mac, version))

        return jsonify({'new_version': client.version, 'filename': client.filename})

    @app.route('/api/v1/product/verify', methods=['GET'])
    def verify():
        mac = request.args.get("mac")
        version = request.args.get("version")
        server = request.args.get("server")

        code = 0
        if client.mac_addr_list is not None:
            result = 'MAC address verified successfully' if mac in client.mac_addr_list else 'MAC address verified failure'
            code = 0 if mac in client.mac_addr_list else 1
        else:
            result = 'No MAC address file'
            code = 2

        client.callback_signal.emit({'type': 'verify', 'content': {'version': version, 'mac': mac, 'code': code, 'server': server, 'result': result}})

        logger.info("{} verified, version: {}, server: {}, code: {}".format(mac, version, server, code))

        return jsonify({'code': code, 'msg': result})

    server = ServerThread(app, port)
    server.start()

    logger.info("start server, port: {}, folder: {}, filename: {}".format(port, client.folder, client.filename))


def stop_server():
    global server
    if server is not None:
        server.shutdown()
        server = None

    logger.info("stop the server")

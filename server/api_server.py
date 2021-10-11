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
from threading import Thread

from PyQt5.QtCore import pyqtSignal
from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '哈哈哈'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task')


# Todo
# shows a single todo item and lets you delete a todo item
class Todo(Resource):
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


# TodoList
# shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


class UpgradeConnect(Resource):
    def __init__(self, client):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('version', required=True)
        self.parser.add_argument('mac', required=True)
        self.client = client

    def get(self):
        args = self.parser.parse_args()
        version = args['version']
        mac = args['mac']

        self.client.upgrade_signal.emit({'version': version, 'mac': mac})

        data = {'new_version': '1.0.2', 'bin_url': 'http://192.168.0.1:8000/test.bin'}

        return data, 200


def startServer(debug, port):
    app.run(debug=debug, port=port)


def start_service(debug, port, client):
    ##
    ## Actually setup the Api resource routing here
    ##
    #api.add_resource(TodoList, '/todos')
    #api.add_resource(Todo, '/todos/<todo_id>')

    api.add_resource(UpgradeConnect, '/api/v1/upgrade/connect', resource_class_kwargs={"client": client})

    thread = Thread(target=startServer, args=[debug, port])
    thread.start()


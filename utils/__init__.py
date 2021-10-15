#!/usr/bin/env python
# encoding: utf-8
'''
@author: Jerry Lee
@contact: liweizhong@nekteck.com
@software: Yuanrui
@file: __init__.py.py
@time: 2021/10/13 17:30
@desc:
'''

import logging
import os

logger = logging.getLogger("firmware_upgrade_server")
logger.setLevel(logging.DEBUG)

# rm_file(log_file)
log_path = os.path.join(os.getcwd(), "firmware_upgrade_server.log")

fileHandler = logging.FileHandler(log_path, mode='w')
fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.DEBUG)

# set formatter
formatter = logging.Formatter('[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
consoleHandler.setFormatter(formatter)
fileHandler.setFormatter(formatter)

# add
logger.addHandler(fileHandler)
logger.addHandler(consoleHandler)

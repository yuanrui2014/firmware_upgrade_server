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
import configparser

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

# configuration
basedir = os.getcwd()

# production config takes precedence over env variables

# production config file at ./project/config/production.cfg
config_path = os.path.join(basedir, 'config.cfg')

SUPPORT_UPGRADE = False
FIRMWARE_VERSION = '1.0.1'


# if config file exists, read it:
if os.path.exists(config_path):
    config = configparser.ConfigParser()

    with open(config_path) as configfile:
        config.read_file(configfile)

    try:
        SUPPORT_UPGRADE = config.getboolean('general', 'support_upgrade')
    except (configparser.NoSectionError, configparser.NoOptionError):
        SUPPORT_UPGRADE = False

    try:
        FIRMWARE_VERSION = config.get('general', 'firmware_version')
    except (configparser.NoSectionError, configparser.NoOptionError):
        FIRMWARE_VERSION = '1.0.1'

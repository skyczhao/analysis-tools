#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Log.py
#
# @author chenzhao
# @since 2017-04-25

import logging.handlers
import os
import platform

runtimeEnv = "product"


def mkdirs(path, separator='/'):
    """
    创建目录
    1. xx/file.txt: 创建xx目录
    2. a/b/c: 创建a/b目录
    3. a/b/c/: 创建a/b/c目录

    :param path:
    :return:
    """

    path = path.strip()
    if path[-1] == separator:
        if not os.path.exists(path):
            os.makedirs(path)
    else:
        idx = path.rfind(separator)
        if idx != -1:
            subpath = path[:idx]
            if not os.path.exists(subpath):
                os.makedirs(subpath)

                
# 判断linux/windows
sysStr = platform.system()
USER_HOME = '.'
SEPARATOR = '/'
if sysStr == "Windows":
    USER_HOME = "C:" + os.environ['HOMEPATH']
    SEPARATOR = '\\'
    # print("Call Windows tasks")
elif sysStr == "Linux":
    USER_HOME = os.environ['HOME']
    SEPARATOR = '/'
    # print("Call Linux tasks")
else:
    pass
    # print("Other System tasks")
FILENAME = SEPARATOR.join([USER_HOME, "logs", "analysis-tools", "parrot.log"])
print("LOG DIR: " + FILENAME)
mkdirs(FILENAME, SEPARATOR)


FORMATTER = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

# Set up a specific logger with our desired output level
logger = logging.getLogger('PARROT')
logger.setLevel(logging.INFO)

if runtimeEnv == "product":
    # 生产环境
    # file message handler
    file_handler = logging.handlers.RotatingFileHandler(
        FILENAME,
        maxBytes=1024 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)
else:
    # 非生产环境
    # console message handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)


def debug(tag, msg):
    logger.debug("({}) {}".format(tag, msg), exc_info=False)


def info(tag, msg):
    logger.info("({}) {}".format(tag, msg), exc_info=False)


def warning(tag, msg):
    logger.warning("({}) {}".format(tag, msg), exc_info=False)


def error(tag, msg):
    # error信息默认打开Exception信息
    logger.error("({}) {}".format(tag, msg), exc_info=True)

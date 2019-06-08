#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Dicts
#
# @author tobin
# @since 2018-06-22

"""
词典工具类
"""


def double_set(d, k, v_k, v_v):
    """
    往词典对应key添加k-v

    :param d: 词典
    :param k: 键
    :param v_k: 值的key
    :param v_v: 值的value
    :return:
    """
    if isinstance(d, dict):
        if k not in d:
            d[k] = dict()

        d[k][v_k] = v_v


def append(d, k, v):
    """
    往词典对应key添加值

    :param d: 词典
    :param k: 键
    :param v: 值
    :return:
    """
    if isinstance(d, dict):
        if k not in d:
            d[k] = []

        d[k].append(v)


def add(d, k, v=1):
    """
    词典对应key值数值操作

    :param d: 词典
    :param k: 键
    :param v: 值
    :return:
    """
    if isinstance(d, dict):
        if k not in d:
            d[k] = 0

        d[k] = d[k] + v

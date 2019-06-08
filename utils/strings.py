#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Strings.py
#
# @author chenzhao
# @since 2017-12-02


def stack_values(fields, quote="", holder="%s", separator=","):
    """
    拼接字符串
    (v1, v2, ...) => ((%s, %s,...), (v1, v2...))

    :param fields:    值/字段
    :param quote:     引用符
    :param holder:    占位符
    :param separator: 分隔符
    :return:
    """
    holders = []
    values = []

    if fields is None:
        return None

    for field in fields:
        if field is None:
            continue

        holders.append("{}{}{}".format(quote, holder, quote))
        values.append(field)

    return separator.join(holders), values


def build_pairs(clauses, holder="%s", separator="AND"):
    """
    构建字符串对
    ([f1, v1, like], [f2, v2, >]...) => ((f1 like %s and f2 > %s...), (v1, v2...))

    :param clauses:   [[field, value, operator]]
    :param holder:    占位符
    :param separator: 分隔符
    :return:
    """
    fields = []
    values = []

    for clause in clauses:
        # skip error
        if clause is None:
            continue

        if len(clause) < 2:
            continue

        # connect where clause
        field = clause[0]
        value = clause[1]

        if len(clause) > 2:
            fields.append("{} {} {}".format(field, clause[2], holder))
        else:
            fields.append("{}={}".format(field, holder))
        values.append(value)

    realSeparator = ' {} '.format(separator)
    return realSeparator.join(fields), values


def escape(obj, quote="'"):
    """
    为字符串添加括号, 与strip函数相反的功能

    :param obj:
    :param quote:
    :return:
    """
    return quote + str(obj) + quote

#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Regexs.py
#
# @author chenzhao
# @since 2017-12-22

import re

SRE_MATCH_TYPE = type(re.match("", ""))

chineseNumRegexRules = u'(?P<number>[零一二两三四五六七八九十百千万亿]+)'
numeralMap = {u'零': 0, u'一': 1, u'二': 2, u'两': 2, u'三': 3, u'四': 4, u'五': 5, u'六': 6, u'七': 7, u'八': 8, u'九': 9,
              u'十': 10, u'百': 100, u'千': 1000, u'万': 10000, u'亿': 100000000}

chineseNumRegex = re.compile(chineseNumRegexRules)


def convertChineseNum(sentence):
    """
    句子中的数值转阿拉伯数字

    :param sentence:
    :return:
    """

    def innerChinese2digits(regex):
        # 应对正则替换
        isRegex = False
        text = ""
        if isinstance(regex, SRE_MATCH_TYPE):
            # print(chinese.groupdict())
            text = regex.group()
            isRegex = True
        else:
            text = regex
            isRegex = False

        total = chinese2digits(text)

        # 返回值
        if isRegex:
            return str(total)
        else:
            return total

    return chineseNumRegex.sub(innerChinese2digits, sentence)


def chinese2digits(chinese):
    """
    中文数值转阿拉伯数字

    :param chinese:
    :return:
    """
    # 数值解析
    total = 0
    absoluteBase = 1  # 表示单位：个十百千...
    relativeBase = 1  # 表示单位：个十百千...
    value = 0
    leading = True
    tailing = True
    for i in range(len(chinese) - 1, -1, -1):
        value = numeralMap.get(chinese[i])
        if value < 10:
            if value == 0:
                tailing = False

            total += (value * relativeBase)
            relativeBase *= 10
            leading = False
        else:
            if tailing:  # 应对 一万三 一百三
                realBase = value
                gap = realBase / relativeBase
                total *= gap
            tailing = False

            if value > absoluteBase:
                absoluteBase = value
                relativeBase = value
            else:
                relativeBase = value * absoluteBase
                value = relativeBase
            leading = True

    if leading:  # 应对 十三 十四 十*之类
        total += value

    return total

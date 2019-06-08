#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import pandas as pd

from utils.timer import timer


@timer
def save_excel(sheet, path):
    """
    保存dataframe到excel文件

    # excel最大行列数总结:
    # 在Excel 2010和Excel 2007中, 工作表的大小为: 16,384 列 x 1,048,576 行
    # 在Excel 97-2003 中, 工作表的大小为: 256 列 x 65,536 行
    """
    sheet_shape = sheet.shape
    print("save size: %s" % str(sheet_shape))
    if sheet_shape[0] > 1048576:
        print("row overflow")
        return
    if sheet_shape[1] > 16384:
        print("column overflow")
        return

    # Solved: IllegalCharacterError
    # Solved: UserWarning: Ignoring URL...
    writer = pd.ExcelWriter(path, engine="xlsxwriter", options={'strings_to_urls': False})
    sheet.to_excel(writer, 'Sheet1')
    writer.save()


@timer
def each_row(sheet, parser, step=100):
    """
    表格行处理
    """
    idx = 0
    for key, row in sheet.iterrows():
        flag = parser(idx, key, row)
        if not flag:
            break

        idx += 1
        if idx % step == 0:
            print("current time: %f" % time.time())
            print("current idx: %d" % idx)


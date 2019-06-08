#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time

def timer(f):
    """
    简单计时器
    打印开始时间/结束时间, 并计时
    """
    def wrapper(*args, **kargs):
        start_time = time.time()
        print("# start at %.5f" % start_time)

        try:
            return f(*args, **kargs)
        finally:
            end_time = time.time()
            print("# end at %.5f" % end_time)
            print("total cost: %.5f" % (end_time - start_time))
    return wrapper


class Counter():
    """
    耗时统计
    
    使用方法：
    with Counter():
        FUNC()
    """

    def __enter__(self):
        self.start_time = time.time()
        print("# start at %.5f" % self.start_time)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.end_time = time.time()
        print("# end at %.5f" % self.end_time)
        print("total cost: %.5f" % (self.end_time - self.start_time))

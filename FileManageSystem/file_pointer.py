"""
author:Wenquan Yang
time:2020/6/11 0:09
"""
from config import *


class FilePointer:
    """
    对基本的文件模块做一个扩充，
    将一些基本的配置放出初始化部分使其更加适应我们自定义的文件系统
    目前这这部分是直接硬封装没加扩展，后续看情况加（咕咕
    """

    def __init__(self, mode):
        self._fp = open(DISK_NAME, mode)
        self._fp.seek(DISK_SIZE + 1, 0)
        self._fp.write(b'\x00')
        self._fp.seek(0)

    def seek(self, size):
        self._fp.seek(size)

    def write(self, obj):
        assert isinstance(obj, bytes)
        self._fp.write(obj)

    def read(self, size=512):
        return self._fp.read(size)

    def close(self):
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fp.close()


def file_func(mode):
    """
    文件装饰器，添加此装饰器就不需要关注文件的打开关闭
    :param mode: 读写方式，主要针对初始化磁盘'wb+'和加载磁盘'ab+'
    :return:
    """

    def func_wrapper(func):
        def return_wrapper():
            with FilePointer(mode) as fp:
                res = func(fp)
            return res

        return return_wrapper

    return func_wrapper

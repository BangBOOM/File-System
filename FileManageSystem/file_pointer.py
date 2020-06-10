"""
author:Wenquan Yang
time:2020/6/11 0:09
"""

from config import *


class FilePointer:
    def __init__(self):
        self.fp = open(DISK_NAME, "wb+")

    def seek(self, size, whence=0):
        self.fp.seek(size, whence)

    def write(self, obj):
        assert isinstance(obj, bytes)
        self.fp.write(obj)

    def read(self, size=512):
        self.fp.read(size)

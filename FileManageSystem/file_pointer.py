"""
author:Wenquan Yang
time:2020/6/11 0:09
"""

from config import *


class FilePointer:
    def __init__(self):
        self._fp = open(DISK_NAME, "wb+")
        self._fp.seek(DISK_SIZE + 1)
        self._fp.write(b'\x00')

    def seek(self, size):
        self._fp.seek(size)

    def write(self, obj):
        assert isinstance(obj, bytes)
        self._fp.write(obj)

    def read(self, size=512):
        self._fp.read(size)

    def close(self):
        self._fp.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._fp.close()

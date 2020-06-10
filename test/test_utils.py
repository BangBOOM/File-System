"""
author:Wenquan Yang
time:2020/6/10 2:53
"""

import pickle
from unittest import TestCase
from utils import serializer


class Test(TestCase):
    def test_serializer(self):
        """
        测试序列化切分的正确性，通过序列化切分，在组合反序列化与最开始的原始字符串比对
        :return:
        """
        s = "hello world" * (2 ** 8)
        s_b = b''
        for item in serializer(s):
            s_b += item
        self.assertEqual(s, pickle.loads(s_b))

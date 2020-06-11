"""
author:Wenquan Yang
time:2020/6/12 3:17
"""
from unittest import TestCase
from load_disk import load_disk


class Test(TestCase):
    def test_load_disk(self):
        base_name = load_disk()
        self.assertEqual("base", base_name)

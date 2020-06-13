"""
author:Wenquan Yang
time:2020/6/12 23:20
"""
from unittest import TestCase
from running_pfs import running_pfs_for_test

class Test(TestCase):
    def test_running_pfs(self):
        base_name=running_pfs_for_test()
        self.assertEqual("base", base_name)

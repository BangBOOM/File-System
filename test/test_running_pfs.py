"""
author:Wenquan Yang
time:2020/6/12 23:20
"""
from unittest import TestCase
from unittest.mock import patch
from running_pfs import running_pfs_for_test


class Test(TestCase):
    def test_running_pfs(self):
        with patch('builtins.print') as mocked_print:
            running_pfs_for_test()
            mocked_print.assert_called_with('demo hello ' + ' '.join(["hello" + str(i) for i in range(10)]))


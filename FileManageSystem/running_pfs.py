"""
author:Wenquan Yang
time:2020/6/12 22:50
intro:文件系统实际运行部分
"""
from file_system import file_system_func


@file_system_func
def running_pfs_for_test(fs):
    print(fs.sp)
    pwd_obj = fs.load_pwd_obj()
    return pwd_obj.name


@file_system_func
def running_pfs(fs):
    pass

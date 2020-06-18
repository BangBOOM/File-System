"""
author:Wenquan Yang
time:2020/6/12 22:50
intro:文件系统实际运行部分
"""
import commands
from utils import bar
from file_system import FileSystem
from file_system import file_system_func


@file_system_func
def running_pfs(fs: FileSystem):
    while True:
        bar(fs.current_user_name, fs.get_current_path_name())
        cmd = input().split()
        if cmd[0] == 'exit':
            break
        try:
            func = getattr(commands, cmd[0])
            func(fs, *cmd[1:])
        except AttributeError:
            print("\n命令不支持\n")


def main():
    running_pfs()


if __name__ == '__main__':
    main()

"""
author:Wenquan Yang
time:2020/6/12 22:50
intro:文件系统实际运行部分
"""
from file_system import FileSystem
from file_system import file_system_func
from commands import mkdir, ls


@file_system_func
def running_pfs_for_test(fs):
    pwd_obj = fs.load_pwd_obj()
    return pwd_obj.name


@file_system_func
def running_pfs(fs: FileSystem):
    print("Welcome to the PFS")
    while True:
        print("root@pfs:{}".format(fs.get_current_path_name()))
        cmd = input("> ").split()
        if cmd[0] == "pwd":
            print(fs.pwd())
        elif cmd[0] == 'mkdir':
            mkdir(fs, cmd[1])
        elif cmd[0] == 'ls':
            ls(fs)
        elif cmd[0] == "exit":
            break


def main():
    running_pfs()


if __name__ == '__main__':
    main()

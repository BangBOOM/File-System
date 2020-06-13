"""
author:Wenquan Yang
time:2020/6/12 22:50
intro:文件系统实际运行部分
"""
from file_system import FileSystem
from file_system import file_system_func


@file_system_func
def running_pfs_for_test(fs):
    pwd_obj = fs.load_pwd_obj()
    return pwd_obj.name


@file_system_func
def running_pfs(fs:FileSystem):
    print("Welcome to the PFS")
    while True:
        print("root@pfs:{}".format(fs.get_current_path_name()))
        cmd=input("> ")
        if cmd == "pwd":
            print(fs.pwd())
        elif cmd == 'mkdir':
            '''等待实现'''
            pass
        elif cmd == 'll':
            '''等待实现'''
            pass
        elif cmd == "exit":
            break

def main():
    running_pfs()

if __name__ == '__main__':
    main()



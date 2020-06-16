"""
author:Wenquan Yang
time:2020/6/14 20:18
"""
from file_system import FileSystem
import pickle
from config import *


def useradd(fs: FileSystem, user_id: int):
    """
    添加用户
    :param fs:
    :param user_id:
    :return:
    """
    fs.add_user(user_id)


def mkdir(fs: FileSystem, name: str, user_id=10):
    """
    新建目录
    新建索引对象-->新建目录对象-->将前两者作为键值对加入当前索引对应的目录-->申请空间存放新建的目录
    :param fs:
    :param name: 文件夹名称
    :param user_id: 用户id，用于权限
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag, info = pwd_cat.check_name(name)
    if not flag:
        print(info)
        return

    new_inode = fs.get_new_inode(user_id=user_id)
    pwd_cat.add_new_cat(name=name, inode_id=new_inode.i_no)
    new_cat = fs.get_new_cat(name=name, parent_inode_id=fs.pwd_inode.i_no)
    fs.write_back(new_inode, bytes(new_cat))  # 写回新建目录
    fs.write_back(fs.pwd_inode, bytes(pwd_cat))  # 写回当前目录，因为新建的目录挂载当前目录也被修改了
    new_inode.write_back(fs.fp)


def cd(fs: FileSystem, args: str, user_id=10):
    """
    切换目录,可以多级目录切换
    :param fs:
    :param args: 切换到的目录名
    :param user_id: 用户id，用于权限
    :return:
    """

    def change_dir(name):
        pwd_cat = fs.load_pwd_obj()
        if name == "..":
            target_id = pwd_cat.parent_inode_id
            if target_id == -1:
                return
        elif name == "~":
            target_id = fs.get_base_dir_inode_id()
        else:
            target_id = pwd_cat.get_dir(name)

        if target_id:
            inode = fs.get_inode(target_id)
            fs.write_back_pwd_inode()
            fs.pwd_inode = inode
            if name == "..":
                fs.path_pop()
            elif name == "~":
                fs.path_clear()
            else:
                fs.path_add(fs.get_pwd_cat_name())

    name_list = args.split('/')
    for name in name_list:
        change_dir(name)


def touch(fs: FileSystem, name: str, user_id=10):
    """
    新建文件
    :param fs:
    :param name:
    :param user_id:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag, info = pwd_cat.check_name(name)
    if not flag:
        print(info)
        return

    new_inode = fs.get_new_inode(user_id=user_id)
    new_inode.target_type = 0  # 文件
    pwd_cat.son_files[name] = new_inode.i_no  # 加入文件字典
    # new_cat = fs.get_new_cat(name=name, parent_inode_id=fs.pwd_inode.i_no)
    # fs.write_back(new_inode, bytes(new_cat))
    fs.write_back(fs.pwd_inode, bytes(pwd_cat))
    new_inode.write_back(fs.fp)


def vim(fs: FileSystem, name: str, user_id=10):
    """
    向文件中输入内容，或者是修改文件
    :param fs:
    :param name:
    :param user_id:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        print("{} 文件不存在".format(name))
    if flag == DIR_TYPE:
        print("{} 是文件夹".format(name))
    if flag == FILE_TYPE:
        inode_io = pwd_cat.son_files[name]
        inode = fs.get_inode(inode_id=inode_io)
        s = "world" * (2 ** 8)
        fs.write_back(inode, pickle.dumps(s))
        # print(inode._i_sectors_state)
        inode.write_back(fs.fp)


def more(fs: FileSystem, name: str, user_id=10):
    """
    展示文件
    :param fs:
    :param name:
    :param user_id:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        print("{} 文件不存在".format(name))
    if flag == DIR_TYPE:
        print("{} 是文件夹".format(name))
    if flag == FILE_TYPE:
        inode_io = pwd_cat.son_files[name]
        inode = fs.get_inode(inode_id=inode_io)
        # print(inode._i_sectors_state)
        text = fs.load_files_block(inode)
        print(text)


def tree(fs: FileSystem, depth, user_id=10):
    """
    生成文件目录结构，具体样式百度
    .
    └── test
        ├── css
        ├── img
        │   └── head
        └── js
    :param fs:
    :param depth: 打印的深度
    :param user_id:
    :return:
    """
    pass


def ls(fs: FileSystem):
    """
    打印当前目录下的全部文件
    :param fs:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()
    file_list = pwd_cat.file_name_and_types()
    print(' '.join([item[0] for item in file_list]))


def rm(fs: FileSystem, args: list, user_id=10):
    """
    删除文件
    :param fs:
    :param args: 参数
    :param user_id:
    :return:
    """

    pwd_cat = fs.load_pwd_obj()
    power = False  # 删除力度
    if args[0] == '-r':
        power = True
        name = args[1]
    else:
        name = args[0]

    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        print("文件不存在")
    else:
        inode_id = -1
        if flag == DIR_TYPE:
            if not power:
                print("无法直接删除目录请使用 rm -r dir_name")
                return
            inode_id = pwd_cat.get_dir(name)
        elif flag == FILE_TYPE:

            if not power:
                dose = input(f"rm:是否删除一般文件“{name}”[Y/N]:")
                if dose.lower() != 'y':
                    return
            inode_id = pwd_cat.get_file(name)

        if inode_id != -1:
            fs.free_up_inode(inode_id)

            # 从当前目录中删除并讲当前目录写回
            pwd_cat.remove(name, flag)
            fs.write_back(fs.pwd_inode, bytes(pwd_cat))

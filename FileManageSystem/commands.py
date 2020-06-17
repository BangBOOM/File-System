"""
author:Wenquan Yang
time:2020/6/14 20:18
intro:命令模块
"""
import pickle
from config import *
from file_system import FileSystem


def useradd(fs: FileSystem):
    """
    添加用户，并将用户目录挂载到base/home/下
    :param fs:
    :return:
    """
    if fs.current_user_id != ROOT_ID:
        print("非root用户无权添加账户")
        return
    user_name, user_id = fs.add_user(fs.current_user_id)

    # 通过base目录切换到home目录
    base_cat = fs.load_base_obj()
    home_id = base_cat.get_dir('home')
    home_inode = fs.get_inode(home_id)
    home_cat = home_inode.get_target_obj(fs.fp)

    # 获取新的目录的inode，并添加到home目录中
    new_inode = fs.get_new_inode(user_id=user_id)
    home_cat.add_new_cat(name=user_name, inode_id=new_inode.i_no)

    # 新建新的用户目录
    new_cat = fs.get_new_cat(name=user_name, parent_inode_id=home_id)

    # 写回新建的目录,和home目录
    fs.write_back(new_inode, bytes(new_cat))
    fs.write_back(home_inode, bytes(home_cat))

    # 写回对应的被修改的节点
    new_inode.write_back(fs.fp)
    home_inode.write_back(fs.fp)


def su(fs: FileSystem, username: str):
    """
    切换当前用户指令
    :param fs:
    :param username:
    :return:
    """
    if fs.login(username=username):
        if username != 'root':
            cd(fs, f'~/home/{username}')
        else:
            cd(fs, f'~/{ROOT}')


def mkdir(fs: FileSystem, name: str):
    """
    新建目录
    新建索引对象-->新建目录对象-->将前两者作为键值对加入当前索引对应的目录-->申请空间存放新建的目录
    :param fs:
    :param name: 文件夹名称
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag, info = pwd_cat.check_name(name)
    if not flag:
        print(info)
        return

    new_inode = fs.get_new_inode(user_id=fs.current_user_id)
    pwd_cat.add_new_cat(name=name, inode_id=new_inode.i_no)
    new_cat = fs.get_new_cat(name=name, parent_inode_id=fs.pwd_inode.i_no)
    fs.write_back(new_inode, bytes(new_cat))  # 写回新建目录
    fs.write_back(fs.pwd_inode, bytes(pwd_cat))  # 写回当前目录，因为新建的目录挂载当前目录也被修改了
    new_inode.write_back(fs.fp)


def cd(fs: FileSystem, args: str):
    """
    切换目录,可以多级目录切换
    :param fs:
    :param args: 切换到的目录名
    :return:
    """
    fs.chdir(args)


def touch(fs: FileSystem, name: str):
    """
    新建文件
    :param fs:
    :param name:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag, info = pwd_cat.check_name(name)
    if not flag:
        print(info)
        return

    new_inode = fs.get_new_inode(user_id=fs.current_user_id)
    new_inode.target_type = 0  # 文件
    pwd_cat.son_files[name] = new_inode.i_no  # 加入文件字典
    # new_cat = fs.get_new_cat(name=name, parent_inode_id=fs.pwd_inode.i_no)
    # fs.write_back(new_inode, bytes(new_cat))
    fs.write_back(fs.pwd_inode, bytes(pwd_cat))
    new_inode.write_back(fs.fp)


def vim(fs: FileSystem, name: str):
    """
    向文件中输入内容，或者是修改文件
    :param fs:
    :param name:
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
        inode.write_back(fs.fp)


def more(fs: FileSystem, name: str):
    """
    展示文件
    :param fs:
    :param name:
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


def tree_x(fs: FileSystem, depth: int, level=0):
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
    :param level: 已经到达的文件深度
    :return:
    """
    if depth == 0:
        return
    pwd_cat = fs.load_pwd_obj()  # 获取当前目录
    file_list = pwd_cat.file_name_and_types()
    for name, flag in file_list:
        if flag == DIR_TYPE:  # 文件夹
            print("│   " * level, end="")
            print("├──", name)
            cd(fs, name)
            tree_x(fs, depth - 1, level + 1)
            cd(fs, "..")
        if flag == FILE_TYPE:  # 文件
            print("│   " * level, end="")
            print("├──", name)


def tree(fs: FileSystem, args: list):
    depth = 1
    if args:
        if args[0] == '-d':
            depth = int(args[1])
    if depth < 1:
        depth = 1
    tree_x(fs, depth)


def ls(fs: FileSystem):
    """
    打印当前目录下的全部文件
    :param fs:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()
    file_list = pwd_cat.file_name_and_types()
    print(' '.join([item[0] for item in file_list]))


def rm(fs: FileSystem, args: list):
    """
    删除文件
    :param fs:
    :param args: 参数
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

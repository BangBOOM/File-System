"""
author:Wenquan Yang
time:2020/6/14 20:18
intro:命令模块
"""
import pickle
from config import *
from utils import check_auth
from utils import color
from file_system import FileSystem
from file_ui import TextEdit


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

    if not home_cat:
        return

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


def pwd(fs: FileSystem):
    print(fs.pwd())


def clear(fs: FileSystem):
    fs.clear()


def cls(fs: FileSystem):
    fs.clear()


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
    if name == '-h':
        print("""
        新建文件夹
            获得当前目录对象pwd_obj
            检查命名冲突，pwd_obj.check_name(name)
            获取新的inode对象
            将新建文件夹的名字和inode号作为键值对写回pwd_obj
            写回新建的目录对象new_obj，并且将其开辟的新的地址块号添加到对应的inode对象中
            写回新的inode对象
        """)
        return

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


def cd(fs: FileSystem, *args: str):
    """
    切换目录,可以多级目录切换
    :param fs:
    :param args: 切换到的目录名
    :return: True/False 表示切换是否完全成功
    """
    if args[0] == '-h':
        print("""
        切换目录
            dirName:要切换到的目标目录名
            cd hello 切换一级目录
            cd hello\hello 切换多级目录
            cd ..\.. 切换上层目录
            cd ~ 切换到根目录
        """)
    else:
        fs.chdir(args[0])


def cp(fs: FileSystem, *args):
    """
    复制文件/目录参数-r
    :param fs:
    :param args:
    :return:
    """
    if args[0] == '-r':
        path_src = args[1]
        path_tgt = args[2]
    else:
        path_src = args[0]
        path_tgt = args[1]


def mv(fs: FileSystem, *args):
    """
    剪切文件或目录     mv home/ywq/demo home/caohang
    :param fs:
    :param args:
    :return:
    """
    path_src = args[0]  # home/ywq/demo
    path_tgt = args[1]  # home/caohang
    name = path_src.split('/')[-1]  #取出文件名
    cnt1 = len(path_src.split('/')) - 1  #第一个目录的深度
    cnt2 = len(path_tgt.split('/'))  #第二个目录的深度
    inode_io = 0
    #删掉原来的目录
    cd(fs, '/'.join(path_src.split('/')[:-1]))
    pwd_cat = fs.load_pwd_obj() #当前目录块
    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        print("{} 文件不存在".format(name))
        cd(fs, '/'.join(['..'] * cnt1))
        return
    else:
        if flag == FILE_TYPE:
            inode_io = pwd_cat.son_files[name]
            del pwd_cat.son_files[name]
        if flag == DIR_TYPE:
            inode_io = pwd_cat.son_dirs[name]
            del pwd_cat.son_dirs[name]
        fs.write_back(fs.pwd_inode, bytes(pwd_cat))
    cd(fs, '/'.join(['..'] * cnt1))

    #增加到现在的目录下
    cd(fs, '/'.join(path_tgt.split('/')))
    pwd_cat_new = fs.load_pwd_obj()  #要增加的目录块
    if flag == FILE_TYPE:
        pwd_cat_new.son_files[name] = inode_io
    if flag == DIR_TYPE:
        inode = fs.get_inode(inode_io)
        new_cat = inode.get_target_obj(fs.fp)
        new_cat.parent_inode_id = fs.pwd_inode.i_no
        pwd_cat_new.son_dirs[name] = inode_io
    fs.write_back(fs.pwd_inode, bytes(pwd_cat_new))
    cd(fs, '/'.join(['..'] * cnt2))


def rename(fs: FileSystem, name1, name2):
    """
    修改名字 rename name1 name2
    :param fs:
    :param name1: 当前文件或目录的名字
    :param name2: 目标名字
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag = pwd_cat.is_exist_son_files(name1)
    if flag == -1:
        print("{} 文件不存在".format(name1))
    else:
        if name2 in pwd_cat.son_files or name2 in pwd_cat.son_dirs:
            print("{} 文件重名".format(name2))
        else:
            if flag == FILE_TYPE:
                pwd_cat.son_files[name2] = pwd_cat.son_files[name1]
                del pwd_cat.son_files[name1]
            if flag == DIR_TYPE:
                pwd_cat.son_dirs[name2] = pwd_cat.son_dirs[name1]
                del pwd_cat.son_dirs[name1]
            fs.write_back(fs.pwd_inode, bytes(pwd_cat))

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
        touch(fs, name)
        vim(fs, name)
        return
    if flag == DIR_TYPE:
        print("{} 是文件夹".format(name))
    if flag == FILE_TYPE:
        inode_io = pwd_cat.son_files[name]
        inode = fs.get_inode(inode_id=inode_io)
        if check_auth(inode.user_id, fs.current_user_id):
            flag, s = fs.load_files_block(inode)
            if not s:
                s = ''
            te = TextEdit(s)
            te.run()
            s = te.s
            fs.write_back(inode, pickle.dumps(s))
            inode.write_back(fs.fp)
        else:
            print("cannot edit file .: Permission denied")


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
        flag, text = fs.load_files_block(inode)
        if flag:
            print(text)
        else:
            print("cannot open file .: Permission denied")


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
            print("├──", color(name, DIR_COLOR_F, DIR_COLOR_B))
            flag_x = fs.ch_sig_dir(name, info=False)
            if flag_x:
                tree_x(fs, depth - 1, level + 1)
                fs.ch_sig_dir("..")
        if flag == FILE_TYPE:  # 文件
            print("│   " * level, end="")
            print("├──", color(name, FILE_COLOR_F, FILE_COLOR_B))


def tree(fs: FileSystem, *args):
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
    for name, flag in file_list:
        if flag == DIR_TYPE:
            print(color(name, DIR_COLOR_F, DIR_COLOR_B), end=' ')
        elif flag == FILE_TYPE:
            print(color(name, FILE_COLOR_F, FILE_COLOR_B), end=' ')
    print()


def ll(fs: FileSystem):
    """
    打印当前目录下的具体信息
    :param fs:
    :return:
    """
    pass


def rm(fs: FileSystem, *args):
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
            flag_x = fs.free_up_inode(inode_id)
            if flag_x:
                # 从当前目录中删除并将当前目录写回
                pwd_cat.remove(name, flag)
                fs.write_back(fs.pwd_inode, bytes(pwd_cat))
            else:
                print("cannot delete directory/file .: Permission denied")

"""
author:Wenquan Yang
time:2020/6/14 20:18
intro:命令模块
"""
import pickle
from threading import Thread
from config import *
from utils import check_auth
from utils import color
from utils import line
from file_system import FileSystem
from file_ui import TextEdit


def useradd(fs: FileSystem, *args):
    """
    添加用户，并将用户目录挂载到base/home/下
    :param fs:
    :return:
    """
    if args and args[0] == '-h':
        print("""
        添加用户
            使用方法直接输入useradd不需要参数
            只有root用户可以使用此命令
            添加完用户后会在base/home/下新建对应的用户文件目录
            命名为用户名
        """)
        return

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


@line
def pwd(fs: FileSystem, *args):
    """
    打印当前目录的完整路径
    :param fs:
    :return:
    """
    print(fs.pwd())


def clear(fs: FileSystem, *args):
    """
    清空终端输出
    :param fs:
    :return:
    """
    fs.clear()


def cls(fs: FileSystem, *args):
    fs.clear()


def su(fs: FileSystem, *args):
    """
    切换当前用户指令
    :param fs:
    :param username:
    :return:
    """
    username = args[0]
    if username == '-h':
        print("""
        切换用户
            su username
            root用户切换其他账户不需要密码
            普通账户切换需要输入密码
        """)
        return

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
            mkdir dirname
            只可以在当前目录的新建不可跳级新建
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
    if args[0] == '-h':
        print("""
        复制文件
            cp xx/xx/src_filename xx/xx/tgt_dir
            复制文件到其他目录
            支持跨目录层级调用
            仅支持复制文件
        """)
        return

    if args[0] == '-r':
        path_src = args[1]
        path_tgt = args[2]
    else:
        path_src = args[0]
        path_tgt = args[1]
        name = path_src.split('/')[-1]  # 取出文件名
        cnt1 = len(path_src.split('/')) - 1  # 第一个目录的深度
        cnt2 = len(path_tgt.split('/'))  # 第二个目录的深度
        text_copy = ""  # 文件内容
        cd(fs, '/'.join(path_src.split('/')[:-1]))
        pwd_cat = fs.load_pwd_obj()
        flag = pwd_cat.is_exist_son_files(name)
        if flag == -1:
            print("{} 文件不存在".format(name))
            cd(fs, '/'.join(['..'] * cnt1))
            return
        else:
            if flag == FILE_TYPE:
                inode_io = pwd_cat.son_files[name]
                inode = fs.get_inode(inode_id=inode_io)
                flag2, text = fs.load_files_block(inode)
                if flag2:
                    text_copy = text  # 传递内容
            if flag == DIR_TYPE:
                print("不能复制文件夹")
                cd(fs, '/'.join(['..'] * cnt1))
                return

        cd(fs, '/'.join(['..'] * cnt1))
        # 增加到现在的目录下
        cd(fs, '/'.join(path_tgt.split('/')))
        touch(fs, name)
        pwd_cat_new = fs.load_pwd_obj()
        new_inode_io = pwd_cat_new.son_files[name]
        new_inode = fs.get_inode(inode_id=new_inode_io)
        fs.write_back(new_inode, pickle.dumps(text_copy))
        new_inode.write_back(fs.fp)
        cd(fs, '/'.join(['..'] * cnt2))


def mv(fs: FileSystem, *args):
    """
    剪切文件或目录     mv home/ywq/demo home/caohang
    :param fs:
    :param args:
    :return:
    """
    if args[0] == '-h':
        print("""
        剪切文件或目录：
            mv xx/xx/src xx/xx/tgt
            可以跨目录层级剪切目录或文件到其他目录
        """)
        return

    path_src = args[0]  # home/ywq/demo
    path_tgt = args[1]  # home/caohang
    name = path_src.split('/')[-1]  # 取出文件名
    cnt1 = len(path_src.split('/')) - 1  # 第一个目录的深度
    cnt2 = len(path_tgt.split('/'))  # 第二个目录的深度
    inode_io = 0
    # 删掉原来的目录
    cd(fs, '/'.join(path_src.split('/')[:-1]))
    pwd_cat = fs.load_pwd_obj()  # 当前目录块
    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        print("{} 文件不存在".format(name))
        cd(fs, '/'.join(['..'] * cnt1))
        return
    else:
        if flag == FILE_TYPE:
            inode_io = pwd_cat.son_files[name]
        if flag == DIR_TYPE:
            inode_io = pwd_cat.son_dirs[name]
        pwd_cat.remove(name, flag)
        fs.write_back(fs.pwd_inode, bytes(pwd_cat))
    cd(fs, '/'.join(['..'] * cnt1))

    # 增加到现在的目录下
    cd(fs, '/'.join(path_tgt.split('/')))
    pwd_cat_new = fs.load_pwd_obj()  # 要增加的目录块
    if flag == FILE_TYPE:
        pwd_cat_new.add_new_file(name, inode_io)
    if flag == DIR_TYPE:
        inode = fs.get_inode(inode_io)
        new_cat = inode.get_target_obj(fs.fp)
        new_cat.parent_inode_id = fs.pwd_inode.i_no
        pwd_cat_new.add_new_cat(name, inode_io)
        fs.write_back(inode, bytes(new_cat))
    fs.write_back(fs.pwd_inode, bytes(pwd_cat_new))
    cd(fs, '/'.join(['..'] * cnt2))


def rename(fs: FileSystem, *args):
    """
    修改名字 rename name1 name2
    :param fs:
    :param args:
    :return:
    """
    if args[0] == '-h':
        print("""
        修改名字
            rename src_name tgt_name
            不可跨目录层级使用
            可以修改文件/目录的名字
        """)
        return

    name1 = args[0]
    name2 = args[1]

    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag = pwd_cat.is_exist_son_files(name1)
    if flag == -1:
        print("{} 文件不存在".format(name1))
    else:
        if name2 in pwd_cat.son_files or name2 in pwd_cat.son_dirs:
            print("{} 文件重名".format(name2))
        else:
            if flag == FILE_TYPE:
                pwd_cat.add_new_file(name2, pwd_cat.son_files[name1])
            if flag == DIR_TYPE:
                pwd_cat.add_new_cat(name2, pwd_cat.son_dirs[name1])
            pwd_cat.remove(name1, flag)
            fs.write_back(fs.pwd_inode, bytes(pwd_cat))


def touch(fs: FileSystem, name: str):
    """
    新建文件
    :param fs:
    :param name:
    :return:
    """
    if name == '-h':
        print("""
        新建文件
            touch file_name
            不可跨目录层级调用
        """)
        return

    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag, info = pwd_cat.check_name(name)
    if not flag:
        print(info)
        return

    new_inode = fs.get_new_inode(user_id=fs.current_user_id)
    new_inode.target_type = 0  # 文件
    pwd_cat.add_new_file(name, new_inode.i_no)
    fs.write_back(fs.pwd_inode, bytes(pwd_cat))
    new_inode.write_back(fs.fp)


def vim(fs: FileSystem, name: str):
    """
    向文件中输入内容，或者是修改文件
    :param fs:
    :param name:
    :return:
    """
    if name == '-h':
        print("""
        编辑文件中的内容
            vim file_name
            不可跨层级调用
            命令使用后会打开一个线程单独运行文本编辑器
        """)
        return

    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        touch(fs, name)
        vim(fs, name)
        return
    if flag == DIR_TYPE:
        print("{} 是文件夹".format(name))
    if flag == FILE_TYPE:
        inode_io = pwd_cat.get_file(name)
        inode = fs.get_inode(inode_id=inode_io)
        if check_auth(inode.user_id, fs.current_user_id):
            def func():
                flag_x, s = fs.load_files_block(inode)
                if not s:
                    s = ''
                te = TextEdit(s)
                te.run()
                s = te.s
                if len(pickle.dumps(s)) <= (13 * BLOCK_SIZE - 100):
                    fs.write_back(inode, pickle.dumps(s))
                    inode.write_back(fs.fp)
                else:
                    print("out of size")

            vim_thread = Thread(target=func)
            vim_thread.start()
        else:
            print("cannot edit file .: Permission denied")


@line
def more(fs: FileSystem, name: str):
    """
    展示文件
    :param fs:
    :param name:
    :return:
    """

    if name and name == '-h':
        print("""
        显示文本内容
            more file_name
            不可跨目录层级调用
            完全显示文本内容
        """)
        return

    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag = pwd_cat.is_exist_son_files(name)
    if flag == -1:
        print("{} 文件不存在".format(name))
    if flag == DIR_TYPE:
        print("{} 是文件夹".format(name))
    if flag == FILE_TYPE:
        inode_io = pwd_cat.get_file(name)
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


@line
def tree(fs: FileSystem, *args):
    if args and args[0] == '-h':
        print("""
        打印目录结构
            tree        单独使用打印一层
            tree -d n   指定打印层数
        """)
        return

    depth = 1
    if args:
        if args[0] == '-d':
            depth = int(args[1])
    if depth < 1:
        depth = 1
    tree_x(fs, depth)


@line
def ls(fs: FileSystem, *args):
    """
    打印当前目录下的全部文件
    :param fs:
    :return:
    """
    if args and args[0] == '-h':
        print("""
        打印当前目录下的全部文件
            ls
            绿色表示目录
            白色表示普通文件
        """)
        return

    pwd_cat = fs.load_pwd_obj()
    file_list = pwd_cat.file_name_and_types()
    for name, flag in file_list:
        if flag == DIR_TYPE:
            print(color(name, DIR_COLOR_F, DIR_COLOR_B), end=' ')
        elif flag == FILE_TYPE:
            print(color(name, FILE_COLOR_F, FILE_COLOR_B), end=' ')
    print()


@line
def ll(fs: FileSystem, *args):
    """
    打印当前目录下的具体信息
    :param fs:
    :return:
    """
    if args and args[0] == '-h':
        print("""
        打印当前目录下的全部文件及详细信息
            ll
            绿色表示目录
            白色表示普通文件
            打印内容分别是：
            1.文件数（普通文件是1，目录是其下一级所包含的文件数目）
            2.上次修改日期（2020-06-19 00:22:42）
            3.文件大小 （512B 整数倍）
            4.拥有者的ID
            5.文件/目录 名
        """)
        return
    fs.show_lls_info()


@line
def stat(fs: FileSystem, name):
    if name == '-h':
        print("""
        显示文件详情
            info filename
            不可跨目录层级调用
        """)
        return
    pwd_cat = fs.load_pwd_obj()
    type_x = pwd_cat.is_exist_son_files(name)
    if type_x == -1:
        return
    inode_id = pwd_cat.get_inode_id(name, type_x)
    inode = fs.get_inode(inode_id)
    inode.show_detail_info(fs.fp)


@line
def detail(fs: FileSystem, *args):
    if args and args[0] == '-h':
        print("""
        显示系统信息：
            系统名
            索引块使用情况
            数据块使用情况
        """)
        return
    fs.show()


def rm(fs: FileSystem, *args):
    """
    删除文件
    :param fs:
    :param args: 参数
    :return:
    """
    if args[0] == '-h':
        print("""
        删除文件或目录
            rm filename     删除当前文件
            rm -r dirname   递归删除目录及其下所有内容
            不可跨目录层级调用
        """)
        return

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


def main(*args):
    """
    打印支持的命令
    :return:
    """
    print("""
    这是一个模拟的文件系统
    fms.pfs用于模拟磁盘，会在系统运行的时候加载系统关闭时关闭
    系统中的信息和用户文件都存放于fms.pfs中，系统运行时进行加载
    基于最基本linux中的inode---dir_block---inode---data_block结构
    包含基本的block有superblock，inode，datablock(dirblock,fileblock)
    不同于linux中使用bitmap进行空间分配，本系统使用成组链接法进行分配
    
    支持多用户多级目录，以及用户访问权限划分
    
    支持的命令有 (通过cmd -h 查看使用 例如 (useradd -h,su -h,tree -h,))
        添加用户 useradd
        切换用户 su username
        当前路径 pwd
        清空屏幕 clear(cls)
        新建目录 mkdir dirname
        新建文件 touch filename
        编辑文件 vim filename
        显示文件 more filename
        切换目录 cd targetdir
        复制功能 cp srcname tgtpath
        剪切功能 mv srcname tgtpath
        重命名   rename srcname tgtname
        目录结构 tree -d n
        目录内容 ls
        目录详情 ll
        文件信息 stat filename/dirname
        系统信息 detail
        删除文件 rm [-r] filename/dirname
    """)

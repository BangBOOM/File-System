"""
author:Wenquan Yang
time:2020/6/12 22:30
intro: 文件系统
"""
import os
import getpass
import pickle
from config import *
from utils import form_serializer
from utils import split_serializer
from utils import check_auth
from models import SuperBlock
from models import INode
from models import CatalogBlock
from file_pointer import FilePointer
from user import User


class FileSystem:
    """
    文件系统，负责磁盘中数据的加载与写入
    对整个文件系统所有数据结构以及操作的封装，后续所有功能扩展的调用都从这里调用
    """

    def __init__(self, fp):
        self.fp = fp
        self.load_disk()
        self.sp = self.load_disk()
        self.base_inode = self.get_base_inode()
        self.pwd_inode = self.base_inode
        self.path = ['base']  # 用于存储当前路径，每个文件名是一个item
        self.current_user_id = ROOT_ID
        self.current_user_name = 'root'
        self.user_counts = 0

    def __enter__(self):
        self.clear()
        self.login()
        self.show_info()
        if self.current_user_name != ROOT:
            self.chdir(f'home/{self.current_user_name}')
        else:
            self.chdir(f'{ROOT}')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理，退出的时候写回超级块，根节点inode，当前节点inode
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.sp.write_back(self.fp)
        self.base_inode.write_back(self.fp)
        self.pwd_inode.write_back(self.fp)

    def ch_sig_dir(self, name, info=True):
        """
        单级目录切换
        :param name:
        :return:
        """
        pwd_cat = self.load_pwd_obj()
        if name == "..":
            target_id = pwd_cat.parent_inode_id
            if target_id == -1:
                return False
        elif name == "~":
            target_id = self.get_base_dir_inode_id()
        else:
            target_id = pwd_cat.get_dir(name)

        if target_id:
            inode = self.get_inode(target_id)

            if not check_auth(inode.user_id, self.current_user_id):
                if self.current_user_id != ROOT_ID:
                    if name not in [*INIT_DIRS, "~"]:
                        if name == '..' and self.path[-2] in [*INIT_DIRS, BASE_NAME]:
                            pass
                        else:
                            if info:
                                print("cannot open directory .: Permission denied")
                            return False
            self.write_back_pwd_inode()
            self.pwd_inode = inode
            if name == "..":
                self.path_pop()
            elif name == "~":
                self.path_clear()
            else:
                self.path_add(self.get_pwd_cat_name())
            return True
        return False

    def chdir(self, args):
        """
        切换目录
        :param args:
        :return:
        """
        name_list = args.split('/')
        for name in name_list:
            if not self.ch_sig_dir(name):
                break

    def _get_password_file_inode_id(self):
        base_cat = self.load_base_obj()
        target_id = base_cat.get_dir('etc')
        target_inode = self.get_inode(target_id)
        target_dir = target_inode.get_target_obj(self.fp)
        password_file_inode_id = target_dir.get_file('password')
        return password_file_inode_id

    def _create_password_file(self):
        pwd_cat = self.load_pwd_obj()
        target_id = pwd_cat.get_dir('etc')
        target_inode = self.get_inode(target_id)
        target_dir = target_inode.get_target_obj(self.fp)
        new_inode = self.get_new_inode(user_id=ROOT_ID, file_type=FILE_TYPE)
        target_dir.add_new_file('password', new_inode.i_no)
        self.write_back(target_inode, bytes(target_dir))
        target_inode.write_back(self.fp)
        new_inode.write_back(self.fp)
        return new_inode.i_no

    def _init_root_user(self):
        print("系统初始状态未创建创建root用户请设置密码")
        flag = 3
        password1 = 'admin'
        while flag > 0:
            password1 = getpass.getpass("输入密码:")
            password2 = getpass.getpass("确认密码:")
            if password1 == password2:
                break
            else:
                print("两次密码不一致重新输入")
            flag -= 1
        root = User(name='root', password=password1, user_id=ROOT_ID)
        password_file_inode_id = self._create_password_file()
        password_file_inode = self.get_inode(inode_id=password_file_inode_id)
        self.write_back(password_file_inode, pickle.dumps([root]))
        password_file_inode.write_back(self.fp)
        return password_file_inode_id

    def login(self, username=None):
        """
        登录模块
        :return:
        """
        password_file_inode_id = self._get_password_file_inode_id()
        if not password_file_inode_id:
            password_file_inode_id = self._init_root_user()
        password_inode = self.get_inode(password_file_inode_id)
        password_list = password_inode.get_target_obj(self.fp)
        self.user_counts = len(password_list)
        if not username:
            flag = 3
            while flag > 0:
                username = input("用户名:")
                password = getpass.getpass("密码:")
                for item in password_list:
                    assert isinstance(item, User)
                    if item.login(username, password):
                        self.current_user_id = item.user_id
                        self.current_user_name = item.name
                        return True
                flag -= 1
                print("用户名或密码错误")
            exit(0)
        else:
            password = None
            if self.current_user_id != ROOT_ID:
                password = getpass.getpass("密码:")
            for item in password_list:
                assert isinstance(item, User)
                if item.login(username, password, root_user=True):
                    self.current_user_id = item.user_id
                    self.current_user_name = item.name
                    return True
            print("用户名或密码错误")
            return False

    def show_ll_info(self):
        """
        打印当前目录下的详细文件信息
        :return:
        """
        pwd_cat = self.load_pwd_obj()
        for name, inode_id in pwd_cat.son_list():
            inode = self.get_inode(inode_id)
            res = inode.show_ll_info(self.fp)
            print(' '.join(res) + ' ' + name)

    def add_user(self, user_id):
        if not check_auth(ROOT_ID, user_id):
            print("非root账户无权新建账户")
            return
        password_file_inode_id = self._get_password_file_inode_id()
        password_inode = self.get_inode(password_file_inode_id)
        password_list = password_inode.get_target_obj(self.fp)
        flag = 3
        username = 'user' + str(self.user_counts)
        password = 'admin'
        while flag > 0:
            username = input("输入用户名:")
            for item in password_list:
                if username == item.name:
                    print("用户名重复")
                    flag -= 1
                    continue
            password1 = getpass.getpass("输入密码:")
            password2 = getpass.getpass("确认密码:")
            if password1 != password2:
                print("密码不一致")
                flag -= 1
                continue
            else:
                password = password1
                break
        password_list.append(User(username, password, self.user_counts))
        self.user_counts += 1
        self.write_back(password_inode, pickle.dumps(password_list))
        return username, self.user_counts - 1

    def get_base_dir_inode_id(self):
        return self.sp.base_dir_inode_id

    def get_current_path_name(self):
        return self.path[-1]

    def pwd(self):
        return '/'.join(self.path)

    def load_disk(self):
        """
        加载磁盘，获取超级块
        :return:
        """
        self.fp.seek(0)
        return SuperBlock.form_bytes((form_serializer(self.fp, SUPER_BLOCK_NUM)))  # 加载超级块

    def path_clear(self):
        while len(self.path) > 1:
            self.path.pop(-1)

    def path_add(self, name):
        self.path.append(name)

    def path_pop(self):
        self.path.pop(-1)

    def get_base_inode(self):
        """
        获取根目录的inode
        :return: INode
        """
        base_inode_id = self.sp.base_dir_inode_id  # 读取超级块中保存的base节点的块号
        self.fp.seek((INODE_BLOCK_START_ID + base_inode_id) * BLOCK_SIZE)
        return INode.form_bytes(self.fp.read())  # 根据块号加载根目录的inode

    def load_pwd_obj(self):
        """
        获取当前inode对应的对象
        :return: CatalogBlock
        """
        return self.pwd_inode.get_target_obj(self.fp)

    def load_base_obj(self):
        """
        获取base_inode对应的目录对象
        :return:
        """
        return self.base_inode.get_target_obj(self.fp)

    def load_files_block(self, inode: INode):
        """
        获取对应inode文件的内容
        :return:反序列化的内容
        """
        if check_auth(inode.user_id, self.current_user_id):
            return True, inode.get_target_obj(self.fp)
        else:
            return False, None

    def get_pwd_cat_name(self):
        """
        获取当前inode对应的目录的名称
        :return:
        """
        return self.load_pwd_obj().name

    def get_new_inode(self, user_id=10, file_type=DIR_TYPE):
        """
        获取新的inode
        :return:inode对象
        """
        inode_id = self.sp.get_free_inode_id(self.fp)
        return INode(i_no=inode_id, user_id=user_id, target_type=file_type)

    def get_inode(self, inode_id):
        """
        获取inode对象
        :param inode_id:
        :return:
        """
        self.fp.seek((INODE_BLOCK_START_ID + inode_id) * BLOCK_SIZE)
        inode = INode.form_bytes(self.fp.read())
        return inode

    @staticmethod
    def get_new_cat(name, parent_inode_id):
        return CatalogBlock(name, parent_inode_id)

    def write_back(self, inode: INode, serializer: bytes):
        """
        申请空闲的数据块并将id添加到inode的栈中
        写回新建的目录或者是文本
        :param inode:
        :param serializer:
        :return:
        """
        assert isinstance(serializer, bytes)
        i_sectors = inode.i_sectors
        k = 0
        inode.clear()
        for item in split_serializer(serializer):
            if i_sectors[k] != -1:
                data_block_id = i_sectors[k]
            else:
                data_block_id = self.sp.get_data_block_id(self.fp)
            inode.add_block_id(data_block_id)
            self.fp.seek((data_block_id + DATA_BLOCK_START_ID) * BLOCK_SIZE)
            self.fp.write(item)
            self.fp.seek((data_block_id + DATA_BLOCK_START_ID) * BLOCK_SIZE)
            k += 1

        # 如果有多余的则释放空间
        for block_id in i_sectors[k:]:
            if block_id == -1:
                break
            self.sp.free_up_data_block(self.fp, block_id)

    def write_back_pwd_inode(self):
        """
        写回当前的pwd_inode
        :return:
        """
        self.pwd_inode.write_back(self.fp)

    def free_up_inode(self, inode_id: int):
        """
        释放文件对应的inode，同时级联释放inode指向的空间
        如果指向的是inode指向的是目录则递归删除
        :return:
        """
        inode = self.get_inode(inode_id)
        if not check_auth(inode.user_id, self.current_user_id):
            return False
        if inode.target_type == DIR_TYPE:
            inode_target = inode.get_target_obj(self.fp)
            for son_inode_id in inode_target.get_all_son_inode():
                self.free_up_inode(son_inode_id)
        for i in range(inode.i_sectors_state):
            self.sp.free_up_inode_block(self.fp, inode.get_sector(i))
        return True

    def show_info(self):
        self.clear()
        print("Welcome to the PFS")
        print(LOGO)

    def clear(self):
        os.system('cls')


def file_system_func(func):
    """
    文件系统的装饰器包装上下文管理器，简化实际编写的时候的代码不需要使用with直接在函数上加个装饰器即可
    :param func:
    :return:
    """

    def func_wrapper():
        with FilePointer('rb+') as fp:
            with FileSystem(fp) as fs:
                res = func(fs)
        return res

    return func_wrapper

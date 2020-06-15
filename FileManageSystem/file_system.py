"""
author:Wenquan Yang
time:2020/6/12 22:30
"""
import getpass
import pickle
from config import *
from utils import form_serializer
from utils import split_serializer
from models import SuperBlock
from models import INode
from models import CatalogBlock
from file_pointer import FilePointer
from user import User


class FileSystem:
    """
    文件系统，负责磁盘的加载与写入
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
        self.login()
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

    def _get_password_file_inode_id(self):
        pwd_cat = self.load_pwd_obj()
        target_id = pwd_cat.get_dir('etc')
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
        target_dir.son_files['password'] = new_inode.i_no  # 加入文件字典
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
        password_file_inode = self.get_inode(inode_id=password_file_inode_id, user_id=ROOT_ID)
        self.write_back(password_file_inode, pickle.dumps([root]))
        password_file_inode.write_back(self.fp)
        return password_file_inode_id

    def login(self):
        """
        登录模块
        :return:
        """
        password_file_inode_id = self._get_password_file_inode_id()
        if not password_file_inode_id:
            password_file_inode_id = self._init_root_user()
        password_inode = self.get_inode(password_file_inode_id, ROOT_ID)
        password_list = password_inode.get_target_obj(self.fp)
        self.user_counts = len(password_list)
        flag = 3
        while flag > 0:
            username = input("用户名:")
            password = getpass.getpass("密码:")
            for item in password_list:
                assert isinstance(item, User)
                if item.login(username, password):
                    self.current_user_id = item.user_id
                    self.current_user_name = item.name
                    return
            flag -= 1
            print("用户名或密码错误")

    def add_user(self):
        password_file_inode_id = self._get_password_file_inode_id()
        password_inode = self.get_inode(password_file_inode_id, ROOT_ID)
        password_list = password_inode.get_target_obj(self.fp)
        flag = 3
        username = 'user' + str(self.user_counts)
        password = 'admin'
        while flag > 0:
            user_name = input("user name:")
            for item in password_list:
                if user_name == item.name:
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
        self.write_back(password_inode, password_list)

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

    def load_files_block(self, inode: INode):
        """
        获取对应inode文件的内容
        :return:反序列化的内容
        """
        return inode.get_target_obj(self.fp)

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

    def get_inode(self, inode_id, user_id=10):
        """
        获取inode对象
        :param inode_id:
        :param user_id:
        :return:
        """
        self.fp.seek((INODE_BLOCK_START_ID + inode_id) * BLOCK_SIZE)
        inode = INode.form_bytes(self.fp.read())
        return inode

    def get_new_cat(self, name, parent_inode_id):
        return CatalogBlock(name, parent_inode_id)

    def write_back(self, inode: INode, serializer: bytes):
        """
        申请空闲的数据块并将id添加到inode的栈中
        写回新建的目录或者是文本
        :param serializer:
        :return:
        """
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

    def free_up_inode(self, inode_id: int, user_id=10):
        """
        释放文件对应的inode，同时级联释放inode指向的空间
        如果指向的是inode指向的是目录则递归删除
        :return:
        """
        inode = self.get_inode(inode_id)
        if inode.target_type == DIR_TYPE:
            inode_target = inode.get_target_obj(self.fp)
            for son_inode_id in inode_target.get_all_son_inode():
                self.free_up_inode(son_inode_id)
        for i in range(inode.i_sectors_state):
            self.sp.free_up_inode_block(self.fp, inode.get_sector(i))


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

"""
author:Wenquan Yang
time:2020/6/12 22:30
"""
from config import *
from utils import form_serializer
from models import SuperBlock
from models import INode
from file_pointer import FilePointer


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
        self.path = ['/']  # 用于存储当前路径，每个文件名是一个item

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
        :return: string or CatalogBlock
        """
        return self.pwd_inode.get_target_obj(self.fp)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理，推出的时候写回超级块，根节点inode，当前节点inode
        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.sp.write_back(self.fp)
        self.base_inode.write_back(self.fp)
        self.pwd_inode.write_back(self.fp)


def file_system_func(func):
    """
    文件系统的装饰器包装上下文管理器，简化实际编写的时候的代码不需要使用with直接在函数上加个装饰器即可
    :param func:
    :return:
    """

    def func_wrapper():
        with FilePointer('ab+') as fp:
            with FileSystem(fp) as fs:
                res = func(fs)
        return res

    return func_wrapper

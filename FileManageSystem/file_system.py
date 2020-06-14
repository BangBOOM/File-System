"""
author:Wenquan Yang
time:2020/6/12 22:30
"""
from config import *
from utils import form_serializer
from utils import split_serializer
from models import SuperBlock
from models import INode
from models import CatalogBlock
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
        :return: CatalogBlock
        """
        return self.pwd_inode.get_target_obj(self.fp)

    def get_new_inode(self, user_id=10):
        """
        获取新的inode
        :return:inode对象
        """
        inode_id = self.sp.get_free_inode_id(self.fp)
        return INode(i_no=inode_id, user_id=user_id)

    def get_new_cat(self, name, parent_inode_id):
        return CatalogBlock(name, parent_inode_id)

    def write_back(self, inode: INode, serializer: bytes):
        """
        申请空闲的数据块并将id添加到inode的栈中
        写回新建的目录或者是文本
        :param serializer:
        :return:
        """
        inode.clear()  # 写入需要重新清空inode中的指向栈
        for item in split_serializer(serializer):
            data_block_id = self.sp.get_data_block_id(self.fp)
            self.fp.seek((data_block_id + DATA_BLOCK_START_ID) * 512)
            self.fp.write(item)
            inode.add_block_id(data_block_id)

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

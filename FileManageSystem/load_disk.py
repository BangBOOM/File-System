"""
author:Wenquan Yang
time:2020/6/12 3:04
"""
from models import *
from file_pointer import file_func
from utils import *


@file_func('ab+')
def load_disk(fp):
    """
    磁盘加载，首先加载超级块
    在根据超级块中的信息加载根节点，先返回根节点目录名，后面的实现还待设计
    :param fp: 文件指针
    :return: 返回根目录的名字判断对错，没有问题的话这个程序得到'base'，
    相应的测试文件在test文件夹中可以运行，证明了前面的初始化是正确的
    """
    fp.seek(0)
    sp = SuperBlock.form_bytes((form_serializer(fp, SUPER_BLOCK_NUM)))  # 加载超级块
    base_inode_id = sp.base_dir_inode_id  # 读取超级块中保存的base节点的块号
    fp.seek((INODE_BLOCK_START_ID + base_inode_id) * BLOCK_SIZE)
    base_inode = INode.form_bytes(fp.read())  # 根据块号加载根目录的inode
    base_dir = base_inode.get_target_obj(fp)  # 根据inode加载目录所在的数据块初始化目录对象
    return base_dir.name


if __name__ == '__main__':
    res = load_disk()
    print(res)

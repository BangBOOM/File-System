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
    :return:
    """
    fp.seek(0)
    sp = SuperBlock.form_bytes((form_serializer(fp, SUPER_BLOCK_NUM)))
    base_inode_id = sp.base_dir_inode_id
    fp.seek((INODE_BLOCK_START_ID + base_inode_id) * BLOCK_SIZE)
    base_inode = INode.form_bytes(fp.read())
    base_dir = base_inode.get_target_obj(fp)
    return base_dir.name


if __name__ == '__main__':
    res=load_disk()
    print(res)
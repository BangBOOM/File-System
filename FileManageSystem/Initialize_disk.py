"""
author:Wenquan Yang
time:2020/6/11 1:24
"""
from models import *
from file_pointer import FilePointer
from utils import *


def file(func):
    """
    装饰器，负责自动关闭文件
    :param func: 函数
    :return:
    """

    def func_x():
        with FilePointer() as fp:
            func(fp)

    return func_x


@file
def initialization(fp):
    # 超级块写入
    sp = SuperBlock()
    start = 0
    for item in split_serializer(bytes(sp)):
        if start == SUPER_BLOCK_NUM:
            raise ValueError("超级块大小超出限制")
        fp.seek(start * BLOCK_SIZE)
        fp.write(item)
        start += 1

    # 索引链接写入
    tmp = INODE_BLOCK_NUM
    start = 0
    while tmp > 0:
        if tmp < FREE_NODE_CNT:
            inode_group_link = INodeGroupLink(start, tmp)
        else:
            inode_group_link = INodeGroupLink(start)
        fp.seek((start + INODE_BLOCK_START_ID) * BLOCK_SIZE)
        fp.write(bytes(inode_group_link))
        start += FREE_NODE_CNT
        tmp -= FREE_NODE_CNT

    # 数据块链接写入
    tmp = DATA_BLOCK_NUM
    start = 0
    while tmp > 0:
        if tmp < FREE_BLOCK_CNT:
            block_group_link = BlockGroupLink(start, tmp)
        else:
            block_group_link = BlockGroupLink(start)
        # print((start + DATA_BLOCK_START_ID) * BLOCK_SIZE)
        fp.seek((start + DATA_BLOCK_START_ID) * BLOCK_SIZE)
        fp.write(bytes(block_group_link))
        start += FREE_BLOCK_CNT
        tmp -= FREE_BLOCK_CNT


if __name__ == '__main__':
    initialization()

"""
author:Wenquan Yang
time:2020/6/11 1:24
intro: 磁盘格式化部分
"""
from models import *
from file_pointer import file_func
from utils import *


@file_func('wb')
def initialization(fp):
    # 超级块写入
    sp = SuperBlock()

    # 索引链接写入
    tmp = INODE_BLOCK_NUM
    start = 0
    while tmp > 0:
        sp.inode_unused_cnt -= 1
        if tmp < FREE_NODE_CNT:
            inode_group_link = INodeGroupLink(start, tmp)
        else:
            inode_group_link = INodeGroupLink(start)
        inode_group_link.write_back(fp)
        start += FREE_NODE_CNT
        tmp -= FREE_NODE_CNT

    # 数据块链接写入
    tmp = DATA_BLOCK_NUM
    start = 0
    while tmp > 0:
        sp.block_unused_cnt -= 1
        if tmp < FREE_BLOCK_CNT:
            block_group_link = BlockGroupLink(start, tmp)
        else:
            block_group_link = BlockGroupLink(start)
        block_group_link.write_back(fp)
        start += FREE_BLOCK_CNT
        tmp -= FREE_BLOCK_CNT

    # 初始化一个根目录
    inode_id = sp.get_free_inode_id(fp)
    inode = INode(inode_id, 0)
    dir = CatalogBlock(BASE_NAME)
    for block in split_serializer(bytes(dir)):
        block_id = sp.get_data_block_id(fp)
        inode.add_block_id(block_id)
        fp.seek((block_id + DATA_BLOCK_START_ID) * BLOCK_SIZE)
        fp.write(block)
    inode.write_back(fp)

    # 写入超级块
    sp.base_dir_inode_id = inode_id
    sp.write_back(fp)


if __name__ == '__main__':
    initialization()

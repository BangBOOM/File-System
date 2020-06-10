"""
author:Wenquan Yang
time:2020/6/9 1:36
content:配置文件
"""

BLOCK_SIZE = 512  # 磁盘块大小Bytes
BLOCK_NUM = 2 ** 20  # 磁盘块总数量

SUPER_BLOCK_NUM = 2  # 超级块占用的块数
INODE_BLOCK_NUM = 2 ** 8  # 索引占用的块数
DATA_BLOCK_NUM = BLOCK_NUM - SUPER_BLOCK_NUM - INODE_BLOCK_NUM

INODE_BLOCK_START_ID = SUPER_BLOCK_NUM

DATA_BLOCK_START_ID = SUPER_BLOCK_NUM + INODE_BLOCK_NUM + 1  # 数据块的起始地址

INODE_SIZE = 512  # INODE占用的块区大小

DISK_SIZE = BLOCK_SIZE * BLOCK_NUM  # 磁盘大小
DISK_NAME = "fms_y.pfs"
DIR_NUM = 128  # 每个目录锁包含的最大文件数
FREE_NODE_CNT = 50  # 超级块中空闲节点的最大块数
FREE_BLOCK_CNT = 100  # 超级块中空闲数据块的最大块数

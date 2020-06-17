"""
author:Wenquan Yang
time:2020/6/9 1:36
content:配置文件
"""

BLOCK_SIZE = 512  # 磁盘块大小Bytes
BLOCK_NUM = 1048576  # 磁盘块总数量

SUPER_BLOCK_NUM = 2  # 超级块占用的块数
INODE_BLOCK_NUM = 256  # 索引占用的块数
DATA_BLOCK_NUM = BLOCK_NUM - SUPER_BLOCK_NUM - INODE_BLOCK_NUM

INODE_BLOCK_START_ID = SUPER_BLOCK_NUM

DATA_BLOCK_START_ID = SUPER_BLOCK_NUM + INODE_BLOCK_NUM + 1  # 数据块的起始地址

INODE_SIZE = 512  # INODE占用的块区大小

DISK_SIZE = BLOCK_SIZE * BLOCK_NUM  # 磁盘大小
DISK_NAME = "../fms_y_v2.pfs"
DIR_NUM = 128  # 每个目录锁包含的最大文件数
FREE_NODE_CNT = 50  # 超级块中空闲节点的最大块数
FREE_BLOCK_CNT = 100  # 超级块中空闲数据块的最大块数

BASE_NAME = "base"  # 根目录名

FILE_TYPE = 0  # 文件类型
DIR_TYPE = 1  # 目录类型

ROOT_ID = 0
ROOT = 'root'

INIT_DIRS = ['root', 'home', 'etc']

VERSION = "0.0.2"

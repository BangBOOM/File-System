"""
author:Wenquan Yang
time:2020/6/9 1:35
"""


# 数据结构

class Block:
    pass


class SuperBlock(Block):
    """
    超级块
    """
    pass


class CatalogBlock(Block):
    """
    目录块
    """
    pass


class fileBlock(Block):
    """
    文件块
    """
    pass


class User:
    """
    用户信息模块
    """
    pass


class INode:
    """
    存放文件说明信息和相应标识符的BFD
    """
    pass

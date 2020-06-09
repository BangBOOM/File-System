"""
author:Wenquan Yang
time:2020/6/10 2:35
"""
"""
存放各种工具函数
"""
from config import BLOCK_SIZE
from math import ceil


def serializer(text: str, encoding='utf-8')->list:
    '''
    输入文本，将其转换成按照block大小切分的块
    :param text: 待序列化的文本
    :param encoding: 编码 默认'utf-8'
    :return: list[b'',b'']
    '''
    b_text = bytes(text, encoding=encoding)
    block_num = int(ceil(len(b_text) / BLOCK_SIZE)) # 计算块数向上取整
    yield from [b_text[BLOCK_SIZE * i:BLOCK_SIZE * (i + 1)] for i in range(block_num)]


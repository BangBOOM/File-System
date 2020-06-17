"""
author:Wenquan Yang
time:2020/6/10 2:35
content:各种工具脚本
"""

import pickle
from math import ceil
from config import BLOCK_SIZE, ROOT_ID


def serializer(text: str) -> list:
    """
    输入文本，将其转换成按照block大小切分的块
    :param text: 待序列化的文本
    :return: list[b'',b'']
    """
    b_text = pickle.dumps(text)
    block_num = int(ceil(len(b_text) / BLOCK_SIZE))  # 计算块数向上取整
    yield from [b_text[BLOCK_SIZE * i:BLOCK_SIZE * (i + 1)] for i in range(block_num)]


def split_serializer(b_obj: bytes) -> list:
    """
    输入字节流按照block大小切分
    :param b_text:
    :return:
    """
    block_num = int(ceil(len(b_obj) / BLOCK_SIZE))  # 计算块数向上取整
    yield from [b_obj[BLOCK_SIZE * i:BLOCK_SIZE * (i + 1)] for i in range(block_num)]


def form_serializer(fp, block_num):
    s = b''
    for _ in range(block_num):
        s += fp.read()
    return s


def check_auth(auth_id, user_id):
    return auth_id == user_id or user_id == ROOT_ID

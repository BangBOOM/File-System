"""
author:Wenquan Yang
time:2020/6/10 2:35
content:各种工具脚本
"""
import time
import pickle
from math import ceil
from config import BLOCK_SIZE, ROOT_ID, VERSION


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
    :param b_obj:
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


def color(filename: str, front_color: str, back_color: str):
    filenames = '\33[0;' + front_color + ';' + back_color + 'm' + filename + '\33[0m'
    return filenames


def bar(user_name, current_path):
    time_now = time.strftime(" %H:%M:%S ", time.localtime())
    time_now = color(time_now, "30", "47")
    user_name = color(' ' + user_name + '@PFS ', "37", "40")
    current_path = color(' >' + current_path + ' ', "37", "44")
    version = color(' ' + VERSION + ' ', "31", "42")
    cmd_in = color('> ', "44", "40")
    print(time_now + user_name + version + current_path)
    print(cmd_in, end="")


def logo():
    LOGO1 = '\33[1;34;40m' + "    ____   ______ _____\n   / __ \ / ____// ___/\n"
    LOGO2 = '\33[1;36;40m' + " / /_/ // /_    \__ \\" + "\n"
    LOGO3 = '\33[1;32;40m' + "/ ____// __/   ___/ /\n/_/    /_/     /____/\n\n\33[0m"
    print(LOGO1, LOGO2, LOGO3)


def line(func):
    def return_func(*args):
        print()
        func(*args)
        print()

    return return_func

"""
author:Wenquan Yang
time:2020/6/10 2:53
"""

from unittest import TestCase
from utils import serializer,createfile,serchfile
from model import INode

Inodemap = []

tmp = [
    b'asdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasdda',
    b'sdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddas',
    b'dasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasd',
    b'asddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasddasdasdd']


class Test(TestCase):
    def test_serializer(self):
        res=[]
        for item in serializer("asdasdd" * (2 ** 8)):
            res.append(item)
        self.assertEqual(res, tmp)
#创建
inode1 = INode(5,"home",{})
Inodemap.append(inode1)
tmp1 = createfile("hello",inode1)
inode2 = INode(tmp1[0],tmp1[1],{})
Inodemap.append(inode2)
tmp2 = createfile("log",inode2)
inode3 = INode(tmp1[0],tmp1[1],{})
Inodemap.append(inode3)
print(Inodemap[0].block,Inodemap[1].block,Inodemap[2].i_no)
print(Inodemap[0].i_no,Inodemap[1].i_no,Inodemap[2].i_no)

filename = input(":") #查询文件
inode = inode1
while filename != "/":
    i_num = serchfile(filename,inode)
    flag = 1
    for i in range(len(Inodemap)):
        if Inodemap[i].i_no == i_num:
            flag = 0
            inode = Inodemap[i]
            break
    if flag == 1:
        print("没有文件夹")
    filename = input(":")

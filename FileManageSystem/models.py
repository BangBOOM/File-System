"""
author:Wenquan Yang
time:2020/6/9 1:35
intro:数据结构定义
"""

import pickle
import time
from config import *
from utils import split_serializer


class Block:

    def __bytes__(self):
        """
        序列化当前对象
        :return:返回bytes
        """
        return pickle.dumps(self)

    @staticmethod
    def form_bytes(s: bytes):
        """
        反序列化
        :param s:从文件读取的序列
        :return: 根据序列构建的对象
        """
        try:
            obj = pickle.loads(s)
        except BaseException:
            raise TypeError("字节序列反序列化成Block对象失败")
        return obj

    def write_back(self, fp):
        """
        模块写回
        要求第一步先定位当前块所在的位置使用fp.seek(xxx)
        :param fp:
        :return:
        """
        raise NotImplemented("当前对象未实现write_back方法")


class SuperBlock(Block):
    """
    超级块
    """

    def __init__(self):
        self.inode_cnt = INODE_BLOCK_NUM  # inode 总数量
        self.inode_unused_cnt = INODE_BLOCK_NUM  # inode 空闲数量
        self.block_cnt = DATA_BLOCK_NUM  # 数据块总数量
        self.block_unused_cnt = DATA_BLOCK_NUM  # 数据块空闲数量
        self.valid_bit = False  # True被挂载，False未被挂载
        self.block_size = BLOCK_SIZE
        self.inode_size = INODE_SIZE
        self.block_group_link = BlockGroupLink(0)
        self.node_group_link = INodeGroupLink(0)
        self.base_dir_inode_id = -1  # 根目录的inode_id

    def write_back(self, fp):
        fp.seek(0)
        start = 0
        for item in split_serializer(bytes(self)):
            if start == SUPER_BLOCK_NUM:
                raise ValueError("超级块大小超出限制")
            fp.seek(start * BLOCK_SIZE)
            fp.write(item)
            start += 1

    def get_data_block_id(self, fp):
        """
        申请空闲块
        :return:空闲块id
        """
        if self.block_unused_cnt == 0:
            raise Exception("没有空闲空间了")
        flag, tmp_id = self.block_group_link.get_free_block()

        if flag:  # 有空闲空间
            self.block_unused_cnt -= 1
            return tmp_id

        # 切换空闲栈
        # 写回
        self.block_group_link.write_back(fp)
        del self.block_group_link  # 在内存中删除当前块，这个不必须，gc会自动收了

        # 读取
        db_id = DATA_BLOCK_START_ID + tmp_id
        fp.seek(db_id * BLOCK_SIZE)
        self.block_group_link = BlockGroupLink.form_bytes(fp.read())  # 根据block_id从磁盘读取写回

        return self.get_data_block_id(fp)

    def free_up_data_block(self, fp, block_id):
        """
        释放磁盘块，即将空出的块写回空闲块号栈
        :param fp:
        :param block_id:
        :return:
        """

        if self.block_group_link.has_free_space():
            self.block_group_link.add_to_stack(block_id)
            return

        next_id = self.block_group_link.get_next_stack()

        # 写回
        self.block_group_link.write_back(fp)
        del self.block_group_link  # 在内存中删除当前块，这个不必须，gc会自动收了

        # 读取
        db_id = DATA_BLOCK_START_ID + next_id
        fp.seek(db_id * BLOCK_SIZE)
        self.block_group_link = BlockGroupLink.form_bytes(fp.read())  # 根据block_id从磁盘读取写回

        self.free_up_data_block(fp, block_id)

    def get_free_inode_id(self, fp):
        """
        获得空闲的inode
        :return: 索引id
        """
        if self.inode_unused_cnt == 0:
            raise Exception("没有空闲inode")
        flag, tmp_id = self.node_group_link.get_free_block()

        if flag:  # 有空闲空间
            self.inode_unused_cnt -= 1
            return tmp_id

        # 切换空闲栈
        # 写回
        self.node_group_link.write_back(fp)
        del self.node_group_link  # 在内存中删除当前块，这个不必须，gc会自动收了

        # 读取
        db_id = INODE_BLOCK_START_ID + tmp_id
        fp.seek(db_id * BLOCK_SIZE)
        self.node_group_link = Block.form_bytes(fp.read())  # 根据block_id从磁盘读取写回

        return self.get_free_inode_id(fp)

    def free_up_inode_block(self, fp, block_id):
        if self.node_group_link.has_free_space():
            self.node_group_link.add_to_stack(block_id)
            return

        next_id = self.node_group_link.get_next_stack()

        # 写回
        self.node_group_link.write_back(fp)
        del self.node_group_link  # 在内存中删除当前块，这个不必须，gc会自动收了

        # 读取
        db_id = INODE_BLOCK_START_ID + next_id
        fp.seek(db_id * BLOCK_SIZE)
        self.node_group_link = Block.form_bytes(fp.read())  # 根据block_id从磁盘读取写回

        self.free_up_data_block(fp, block_id)


class INode(Block):
    """
    存储文件的相关信息，用于定位到文件所在的数据块
    """

    def __init__(self, i_no: int, user_id: int, target_type=1):
        """

        :param i_no:    节点块号
        :param user_id: 用户号
        :param target_type: 目标文件的类型
        """
        self._i_no = i_no  # inode编号
        self._write_deny = False  # 写文件，防止多个进程同时对一个文件写
        self._user_id = user_id
        self._group_id = -1
        self._size = 0  # 指向的文件/目录的大小字节数
        self._ctime = time.time()  # inode上一次变动时间，创建时间
        self._mtime = time.time()  # 文件内容上一次变动的时间
        self._atime = time.time()  # 文件上一次打开的时间
        self._i_sectors = [-1] * 13  # 指向的文件/目录所在的数据块
        self._i_sectors_state = 0  # 13块存放数据的栈用了几块
        self._target_type = target_type  # 0指代文件，1指代目录

    def clear(self):
        """
        清空_i_sectors
        :return:
        """
        self._i_sectors_state = 0

    def add_block_id(self, block_id):
        if self._i_sectors_state == 12:
            raise Exception("文件超出大小INode无法存放")
        self._i_sectors[self._i_sectors_state] = block_id
        self._i_sectors_state += 1

    def get_target_obj(self, fp):
        s = b''
        for block_id in self._i_sectors[:self._i_sectors_state]:
            fp.seek((block_id + DATA_BLOCK_START_ID) * BLOCK_SIZE)
            s += fp.read()
        if self.target_type == 1:
            return CatalogBlock.form_bytes(s)
        else:
            return pickle.loads(s)

    @property
    def target_type(self):
        return self._target_type

    @target_type.setter
    def target_type(self, value):
        if value not in (0, 1):
            raise ValueError("输入的文件类型错误")
        self._target_type = value

    @property
    def i_no(self):
        return self._i_no

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, user_id: int):
        if not isinstance(user_id, int):
            raise TypeError("user_id需要int类型")
        self._user_id = user_id

    def get_ctime(self, func):
        return func(self._ctime)

    def update_ctime(self):
        self._ctime = time.time()

    def get_mtime(self, func):
        return func(self._mtime)

    def update_mtime(self):
        self._mtime = time.time()

    def get_atime(self, func):
        return func(self._ctime)

    def update_atime(self):
        self._atime = time.time()

    @property
    def write_deny(self):
        return self._write_deny

    def lock(self):
        """
        加锁
        某个进程修改指向的文件的时候禁止其他进程修改
        :return:
        """
        self._write_deny = True

    def unlock(self):
        """
        释放锁
        进程使用完指向的文件后释放
        :return:
        """
        self._write_deny = False

    def write_back(self, fp):
        db_id = INODE_BLOCK_START_ID + self.i_no
        fp.seek(db_id * BLOCK_SIZE)
        fp.write(bytes(self))


class CatalogBlock(Block):
    """
    目录块
    """

    def __init__(self, name, parent_inode_id=-1):
        """
        初始化目录块
        :param name: 目录名
        """
        self.name = name
        self.parent_inode_id = parent_inode_id  # 上级目录的inode索引的id
        self.son_files = dict()  # key:filename,value:inode_id
        self.son_dirs = dict()

    def add_new_cat(self, name, inode_id):
        self.son_files[name] = inode_id

    def check_name(self, name):
        if name in self.son_dirs or name in self.son_files:
            return False, f"新建的名字{name}已经存在"
        else:
            return True, None

    def file_name_and_types(self):
        return [(key, 1) for key in self.son_dirs.keys()] + [(key, 0) for key in self.son_files.keys()]


class GroupLink(Block):
    def __init__(self, start_block_id, cnt):
        self.block_id = start_block_id
        self._count = cnt
        self.stack = [i for i in range(start_block_id + self.count, start_block_id, -1)]
        if self.count < FREE_BLOCK_CNT:  # 不足成组数目则是最后一组,在栈顶放入0
            self.stack.insert(0, 0)

    @property
    def count(self):
        return self._count

    def get_free_block(self):
        """
        获得一个空闲的id
        :return: 大于0的值表示返回一个正确的
        """
        if self.count > 1:
            self._count -= 1
            return True, self.stack.pop(-1)
        else:
            return False, self.stack[0]

    def has_free_space(self):
        return self.count < FREE_BLOCK_CNT

    def add_to_stack(self, block_id):
        self.stack.append(block_id)
        self._count += 1

    def get_next_stack(self):
        """
        返回指向的下的下一个栈的id
        :return:
        """
        return self.stack[0]


class BlockGroupLink(GroupLink):
    """
    成组分配中的基本块管理一组空闲块
    """

    def __init__(self, start_block_id, cnt=FREE_BLOCK_CNT):
        super().__init__(start_block_id, cnt)

    def write_back(self, fp):
        db_id = DATA_BLOCK_START_ID + self.block_id
        fp.seek(db_id * BLOCK_SIZE)
        fp.write(bytes(self))


class INodeGroupLink(GroupLink):

    def __init__(self, start_block_id, cnt=FREE_NODE_CNT):
        super().__init__(start_block_id, cnt)

    def write_back(self, fp):
        db_id = INODE_BLOCK_START_ID + self.block_id
        fp.seek(db_id * BLOCK_SIZE)
        fp.write(bytes(self))


if __name__ == '__main__':
    ''' 使用seek移动文件指针，在指定位置即指定的块写入相应的数据
    s="asdasdd"*(2**10)
    block=0
    with open("demo1.pfs", 'wb') as f:
        s_b=bytes(s,encoding='utf-8')
        start=0
        while start*1024<len(s_b):
            print(s_b[start*1024:(start+1)*1024])
            f.seek(start*1024,0)
            f.write(s_b[start*1024:(start+1)*1024])
            block+=1
            start+=1
    print(block)
    with open("demo1.pfs",'rb') as f:
        l=b''
        i=0
        while i<block:
            try:
                tmp=f.read(1024)
                print(tmp)
                l+=tmp
                i+=1
                f.seek(1024 * i, 0)
            except:
                break
    '''

    '''  测试对inode节点对象的序列化并存入相应的块中
    obj_list=[INode(10,"hello") for _ in range(10)]
    with open("demo.pfs",'ab+') as f:
        for i,obj in enumerate(obj_list):
            f.seek(1024*i, 0)
            s=f.read(1024)
            print(type(INode.form_bytes(s)))
            f.write(bytes(obj))
        f.write(b'\x00')
    print(l.decode(encoding='utf-8'))
    inode=INode(10,"hello")
    s=bytes(inode)
    print(s)
    print(s.__sizeof__())
    new_s=INode.form_bytes(s)
    print(type(new_s))
    '''

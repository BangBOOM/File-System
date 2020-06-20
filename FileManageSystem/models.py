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

    def show_sp_info(self):
        print("INODE使用情况：", self.inode_unused_cnt, '/', self.inode_cnt)
        print("DATABLOCK使用情况：", self.block_unused_cnt, '/', self.block_cnt)

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
            self.block_unused_cnt += 1
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
            self.inode_unused_cnt += 1
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

    def __init__(self, i_no: int, user_id: int, target_type=DIR_TYPE):
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
        self.user_group = {ROOT_ID, user_id}  # 可访问用户

    def get_sector(self, idx):
        return self._i_sectors[idx]

    def add_block_id(self, block_id):
        if self._i_sectors_state == 12:
            raise Exception("文件超出大小INode无法存放")
        self._i_sectors[self._i_sectors_state] = block_id
        self._i_sectors_state += 1

    def clear(self):
        self._i_sectors = [-1] * 13
        self._i_sectors_state = 0

    def get_target_obj(self, fp):
        if self._i_sectors_state == 0:
            return None
        s = self.get_target_bytes(fp)
        self.update_atime()
        self.write_back(fp)
        if self.target_type == 1:
            return CatalogBlock.form_bytes(s)
        else:
            return pickle.loads(s)

    def get_target_bytes(self, fp):
        s = b''
        for block_id in self._i_sectors[:self._i_sectors_state]:
            fp.seek((block_id + DATA_BLOCK_START_ID) * BLOCK_SIZE)
            s += fp.read()
        return s

    def show_ll_info(self, fp):
        """
        使用ll指令时的单条信息
        :param fp
        :return: str
        """
        count = 1
        if self.target_type == DIR_TYPE:
            target_dir = self.get_target_obj(fp)
            count = target_dir.counts
        time_x = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._mtime))
        size_x = BLOCK_SIZE * self.i_sectors_state
        return str(count), time_x, str(size_x), str(self.user_id)

    def show_detail_info(self, fp):
        """
        使用info name指令时显示的信息
        :return:
        """
        print("INODE_ID:", self.i_no)
        if self.target_type == FILE_TYPE:
            print("类型：文件")
        else:
            print("类型：目录")
        print("拥有者ID:", self.user_id)
        print("创建时间：", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._ctime)))
        print("上一次打开时间：", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._atime)))
        print("上一次修改时间：", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self._mtime)))
        print("size:", len(self.get_target_bytes(fp)))
        print("占用数据块：", self._i_sectors)

    @property
    def i_sectors(self):
        return self._i_sectors

    @property
    def i_sectors_state(self):
        return self._i_sectors_state

    @i_sectors_state.setter
    def i_sectors_state(self, val):
        self._i_sectors_state = val

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

    def update_ctime(self):
        self._ctime = time.time()

    def update_mtime(self):
        self._mtime = time.time()

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
        self._mtime = time.time()  # 修改时间
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
        self.counts = 0

    def son_list(self):
        yield from self.son_files.items()
        yield from self.son_dirs.items()

    def add_new_cat(self, name, inode_id):
        self.son_dirs[name] = inode_id
        self.counts += 1

    def add_new_file(self, name, inode_id):
        self.son_files[name] = inode_id
        self.counts += 1

    def get_dir(self, dir_name):
        """
        获取对应目录的inode_id
        :param dir_name:
        :return:
        """
        return self.son_dirs.get(dir_name)

    def get_file(self, file_name):
        """
        获取对应文件的inode_id
        :param file_name:
        :return:
        """
        return self.son_files.get(file_name)

    def get_inode_id(self, name, type_x):
        if type_x == FILE_TYPE:
            return self.get_file(name)
        if type_x == DIR_TYPE:
            return self.get_dir(name)

    def check_name(self, name):
        """
        检查文件名称是否存在
        :param name:
        :return: 是否存在，message
        """
        if name in self.son_dirs or name in self.son_files:
            return False, f"新建的名字{name}已经存在"
        else:
            return True, None

    def get_all_son_inode(self) -> list:
        """
        返回所有子目录文件的节点
        :return: list
        """
        return [v for _, v in self.son_files.items()] + [v for _, v in self.son_dirs.items()]

    def remove(self, name, flag):
        if flag == FILE_TYPE:
            self.son_files.pop(name)
            self.counts -= 1
        elif flag == DIR_TYPE:
            self.son_dirs.pop(name)
            self.counts -= 1

    def file_name_and_types(self):
        return [(key, DIR_TYPE) for key in self.son_dirs.keys()] \
               + [(key, FILE_TYPE) for key in self.son_files.keys()]

    def is_exist_son_files(self, name):
        """
        :return:1 存在son_files
        :return:0 存在son_dirs
        :return:-1 不存在
        """
        if name in self.son_files:
            return FILE_TYPE
        if name in self.son_dirs:
            return DIR_TYPE
        if name not in self.son_dirs and name not in self.son_files:
            return -1


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

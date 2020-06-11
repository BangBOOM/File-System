"""
author:Wenquan Yang
time:2020/6/9 1:35
"""

# 数据结构
import array
import pickle


class Block:
    pass


class SuperBlock(Block):
    """
    超级块
    """
    pass


class INode:
    """
    存放文件说明信息和相应标识符的BFD
    """

    def __init__(self, i_no: int, name: str,block: dict):
        '''

        :param i_no:    节点块号
        :param name:    指向的文件或目录的名称
        '''
        self.i_no = i_no  # inode编号
        self.name = name
        self.block = block  #用字典表示inode编号和文件名的对应
        self._write_deny = False  # 写文件，防止多个进程同时对一个文件写
        self._i_sectors = array.array('l', [-1] * 13)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not isinstance(name, str):
            raise TypeError("Expected a string")
        self._name = name

    @property
    def write_deny(self):
        return self._write_deny

    def lock(self):
        '''
        加锁
        某个进程修改指向的文件的时候禁止其他进程修改
        :return:
        '''
        self._write_deny = True

    def unlock(self):
        '''
        释放锁
        进程使用完指向的文件后释放
        :return:
        '''
        self._write_deny = False

    def __bytes__(self):
        '''
        序列化当前对象
        :return:返回bytes
        '''
        return pickle.dumps(self)

    @staticmethod
    def form_bytes(s: bytes):
        '''
        反序列化
        :param s:从文件读取的序列
        :return: 根据序列构建的对象
        '''
        try:
            obj=pickle.loads(s)
        except:
            raise ValueError("iNode对象 反序列化失败")
        return obj



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

if __name__=='__main__':

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
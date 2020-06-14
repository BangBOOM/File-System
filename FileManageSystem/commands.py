"""
author:Wenquan Yang
time:2020/6/14 20:18
"""
from file_system import FileSystem


def mkdir(fs: FileSystem, name: str, user_id=10):
    """
    新建目录
    :param fs:
    :param name: 文件夹名称
    :return:
    """
    pwd_cat = fs.load_pwd_obj()  # 当前目录
    flag, info = pwd_cat.check_name(name)
    if not flag:
        print(info)
        return

    new_inode = fs.get_new_inode(user_id=user_id)
    pwd_cat.add_new_cat(name=name, inode_id=new_inode.i_no)
    new_cat = fs.get_new_cat(name=name, parent_inode_id=fs.pwd_inode.i_no)
    fs.write_back(new_inode, bytes(new_cat))  # 写回新建目录
    fs.write_back(fs.pwd_inode, bytes(pwd_cat))  # 写回当前目录，因为新建的目录挂载当前目录也被修改了
    # new_inode.write_back(fs.fp)


def ls(fs: FileSystem):
    """
    打印当前目录下的全部文件
    :param fs:
    :return:
    """
    pwd_cat = fs.load_pwd_obj()
    file_list = pwd_cat.file_name_and_types()
    print(' '.join([item[0] for item in file_list]))
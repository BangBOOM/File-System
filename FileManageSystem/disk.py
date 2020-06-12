@file_func('wb')
def create(fp):
    sp = SuperBlock()
    pwd_inode_id = sp.get_free_inode_id(fp)
    pwd_inode = INode(pwd_inode_id, 10)
    block_id = sp.get_data_block_id(fp)
    pwd_inode._i_sectors[0] = block_id
    print("pwd:",block_id)
    new_inode_id = sp.get_free_inode_id(fp)
    new_inode = INode(new_inode_id,10)
    filename = "hello"
    pwd_inode_catlog = CatalogBlock("home")
    pwd_inode_catlog.son_files[filename] = new_inode_id
    for item in split_serializer(bytes(pwd_inode_catlog)):#把字典写入
        fp.seek(pwd_inode._i_sectors[0] * BLOCK_SIZE)
        fp.write(item)
    #写文件
    s = "world" * (2 ** 8)
    b_text = pickle.dumps(s)
    block_num = int(ceil(len(b_text) / BLOCK_SIZE))
    for i in range(block_num):
        new_inode._i_sectors[i] = sp.get_data_block_id(fp)
        print("new:",new_inode._i_sectors[i])

    k = 0
    for item in serializer(s):
        fp.seek(new_inode._i_sectors[k] * BLOCK_SIZE)
        fp.write(item)
        k += 1
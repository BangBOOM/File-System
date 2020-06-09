# 设计实现

整体结构设想：
1. 比如`main.py`是整个程序的入口
2. `python main.py`开启程序进程
3. 接下来进入用户登录模块，用户登录是单独开辟一个线程（这样就可以模拟多用户登录的情况）

实现步骤：
1. 确定好基本的数据结构
2. 实现基本的文件管理（mkdir,cd,cp,mv,touch,vim),高级的放到后面
3. 用户登录
4. 用户权限


## 进展

2020/6/10

添加了添加了文本切分序列化，具体的就是当一个文件大于一个基本块容量时可以将文本切分成n份，简单实现了INode节点。

基本理清楚了一些结构，学习的文章如下。

学习内容链接：

+ [十六. 文件系统二(创建文件系统)](https://zhuanlan.zhihu.com/p/36754495)
+ [Linux文件系统详解](https://juejin.im/post/5b8ba9e26fb9a019c372e100#heading-13)
+ [Linux文件系统详解](https://www.cnblogs.com/bellkosmos/p/detail_of_linux_file_system.html)
+ [鸟叔linux私房菜中文件系统部分](http://cn.linux.vbird.org/linux_basic/linux_basic.php)


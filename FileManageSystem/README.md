# 设计实现

整体结构设想：
1. 比如`main.py`是整个程序的入口
2. `python main.py`开启程序进程
3. 接下来进入用户登录模块，用户登录是单独开辟一个线程（这样就可以模拟多用户登录的情况）

实现步骤：
1. 确定好基本的数据结构
2. 实现基本的文件管理（mkdir,cd,cp,mv,touch),高级的放到后面
3. 用户登录
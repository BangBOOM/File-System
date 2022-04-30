# 操作系统课程设计

多用户、多级目录结构文件系统的设计与实现。

模拟实现类Linux的文件系统

在Windows环境下开发使用，目前测试MacOS下无法使用完整功能，Linux环境未测试。

## 使用方法

进入[FileManageSystem](FileManageSystem)目录下
1. 运行[initialize_disk.py](FileManageSystem/initialize_disk.py)生成一个固定大小的文件模拟磁盘
2. 在终端中运行[running_pfs.py](FileManageSystem/running_pfs.py) 模拟加载磁盘新建命令行终端
3. 输入`main`指令查看支持的命令

![terminal](terminal.png)


## 文件目录

```txt
C:.                                    
│  fms.pfs  # 磁盘                           
│  README.md                           
│                                      
├─docs                                 
│      bug解决.md                        
│      命令实现.md                         
│      基本知识点.md                        
│      文件系统中的文件结构.md                   
│      空闲块分配.md                        
│                                      
├─FileManageSystem                     
│     commands.py  # 命令的实现类似cd，mv，ll                    
│     config.py    # 基本配置                    
│     file_pointer.py   # 磁盘指针               
│     file_system.py    # 文件系统，命令的实现通过调用这里面的接口               
│     file_ui.py        # 文本编辑的ui界面               
│     initialize_disk.py # 磁盘初始化              
│     main.py                          
│     models.py          # 基本底层数据结构              
│     README.md                        
│     running_pfs.py    # 运行文件系统               
│     user.py           # 用户               
│     utils.py          # 一些的脚本                                                      
│                                      
└─test                   # 测试文件待完善              
        test_models.py                 
        test_running_pfs.py            
        test_utils.py                  
        __init__.py                    
```

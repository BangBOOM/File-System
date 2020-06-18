# 操作系统课程设计

多用户、多级目录结构文件系统的设计与实现。

模拟实现类Linux的文件系统



## git使用规范

提交文件的时候几个规范的写法：

```
init: 初始化项目
try: 尝试完成xxx功能 
add: 添加用xxx功能
update: 完善xx功能
done: 完成xx功能
fix: 修复xxbug
delete: 删除xxx内容
reset: 放弃修改返回
```

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

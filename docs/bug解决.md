# 遇到的一些有价值的bug

## 文件读写问题
发现是在新建文件的时候发现刚新建的也无法读出，期间也在指定的位置即使用seek
移动指针发现即使刚使用write然后再读出也是没有内容的。后来查阅文档发现使用a+模式可以用seek()方法读但是写操作
永远是在文件的末尾。[stack overflow](https://stackoverflow.com/questions/1466000/difference-between-modes-a-a-w-w-and-r-in-built-in-open-function)

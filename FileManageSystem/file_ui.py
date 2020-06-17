import tkinter as tk
from tkinter import scrolledtext


class TextUi:
    # win = tk.Tk()  # 创建窗口
    # win.title('文本编辑器')  # 设置标题


    #text.insert(tk.INSERT, s)  # s为传入的字符串，显示内容

    def __init__(self, s: str):
        self.win = tk.Tk()  # 创建窗口
        self.win.title('文本编辑器')  # 设置标题
        self.s = s
        frame = tk.Frame(self.win, width=300, height=80)
        frame.pack(fill=tk.X, ipady=2, expand=False)
        btn_open = tk.Button(frame, text='取消', command=self.do_cancel)  # 创建按钮用于打开文件
        btn_save = tk.Button(frame, text='保存', command=self.do_save)  # 创建按钮用于保存文件

        # 放置按钮
        btn_open.pack(side=tk.LEFT, anchor=tk.W, ipadx=10)
        btn_save.pack(side=tk.TOP, anchor=tk.E, ipadx=10)

        # 创建滚动多行文本框，用于编辑文件
        self.text = scrolledtext.ScrolledText(self.win, wrap=tk.WORD)
        self.text.pack(side=tk.BOTTOM)

        self.text.insert(tk.INSERT, s)  # s为传入的字符串，显示内容
        self.flag = False

    def run(self):
        self.win.mainloop()  # 进入消息循环


    def do_cancel(self):
        """
        退出，不保存
        """
        self.win.quit()

    def do_save(self):
        """
        保存修改内容
        """
        self.flag = True
        self.s = self.text.get(0.0, tk.END) #获取文本内容
        self.s = self.s.strip()


#TextUi('demo')

# s = "i am"
# s = s + "\n"
# s = s + "a good man"
# #s = s + "\n"
# frame = tk.Frame(win, width=300, height=80)
# frame.pack(fill=tk.X,ipady=2,expand=False)
# btn_open = tk.Button(frame, text='取消', command=do_cancel)  # 创建按钮用于打开文件
# btn_save = tk.Button(frame, text='保存', command=do_save)  # 创建按钮用于保存文件
#
# # 放置按钮
# btn_open.pack(side=tk.LEFT, anchor=tk.W, ipadx=10)
# btn_save.pack(side=tk.TOP, anchor=tk.E, ipadx=10)
#
#
#
# # 创建滚动多行文本框，用于编辑文件
# text = scrolledtext.ScrolledText(win, wrap=tk.WORD)
# text.pack(side=tk.BOTTOM)
#
# text.insert(tk.INSERT, s)  #s为传入的字符串，显示内容


#win.mainloop()  # 进入消息循环
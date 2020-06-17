import tkinter as tk
from tkinter import scrolledtext


class TextEdit:
    def __init__(self, text: str):
        self.win = TextWindow('文本编辑器')
        self.s = text
        self.flag = False
        self.layout(text)

    def layout(self, s):
        frame = tk.Frame(self.win, width=300, height=80)
        frame.pack(fill=tk.X, ipady=2, expand=False)
        btn_save = tk.Button(frame, text='保存', command=self.save)  # 创建按钮用于保存文件

        # 放置按钮
        btn_save.pack(side=tk.TOP, anchor=tk.E, ipadx=10)

        btn_save.configure(font=("Consolas", 16))

        # 创建滚动多行文本框，用于编辑文件
        self.text = scrolledtext.ScrolledText(self.win, wrap=tk.WORD)
        self.text.pack(side=tk.BOTTOM)
        self.text.configure(font=("Consolas", 16))
        self.text.insert(tk.INSERT, s)  # s为传入的字符串，显示内容

    def run(self):
        self.win.mainloop()  # 进入消息循环

    def save(self):
        """
        保存修改内容
        """
        self.flag = True
        self.s = self.text.get(0.0, tk.END)  # 获取文本内容
        self.s = self.s.strip()


class TextWindow(tk.Tk):
    def __init__(self, title):
        super().__init__()
        self.title(title)

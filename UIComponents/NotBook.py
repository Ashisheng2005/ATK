#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/2/22 下午3:18 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : NotBook.py
# @desc : README.md

from tkinter import *
from tkinter import ttk
from UIComponents.RoundedCornerButton import RoundedButton
from UIComponents.ToolTip import ToolTip


class NotBookTable:

    def __init__(self, master=None, image_file=None, **kwargs):
        self.master = master
        self.kw = kwargs

        # 关于选中的状态
        self.select_state = True
        self.frame = Frame(self.master)
        self.shut_button = None
        self.but = None
        self.create_but(image_file)

    def create_but(self, image=None):
        if image:
            image = PhotoImage(file=image)
            photo = Label(self.frame, image=image, text="  ", compound='right')
            photo.image = image
            photo.pack(side=LEFT)

        self.but = Label(self.frame, **self.kw)
        self.but.pack(side=LEFT)
        self.shut_button = RoundedButton(self.frame,
                                         text="×",
                                         radius=120,
                                         height=15,
                                         width=15,
                                         fore_ground="#f0f0f0",
                                         select_foreground="#f0f0f0"
                                         )
        self.shut_button.pack(expand=True)
        tooltip = ToolTip(self.shut_button, "关闭标签页")

        self.frame.pack(side=LEFT)
        return self.but


class NotBook(Frame):

    def __init__(self, master=None):
        super().__init__(master=master)
        self.master = master
        # 标签和窗口的注册表 [(table_id, windows_child)]
        self.tabel_windows = []
        # 选中窗口id
        self.select_id = None
        # 鼠标进入的窗口id
        self.mouse_enter_id = None

        # 上一行的标签框架
        self.table_frame = Frame(self)
        # 下方的窗口框架
        self.windows_frame = Frame(self)
        # 外部定义的方法
        self.user_bind_command = None
        self.placement()

    def placement(self):
        self.table_frame.pack(side=TOP, fill=X)
        self.windows_frame.pack(fill=BOTH, expand=True)

    def get_frame(self):
        """注册一个页面，外部像内部申请一个frame"""
        frame = Frame(self.windows_frame)
        return frame

    def table_find(self, tab_id):
        """查找id位置的工具"""

        if type(tab_id) is int:
            return tab_id

        for i in range(len(self.tabel_windows)):
            if tab_id in self.tabel_windows[i]:
                return i

        else:
            return False

    def tab_id_verification(self, tab_id):
        """对于tab_i"""
        pass

    def shut_windows(self, tab_id):
        # 先执行外部定义的方法，在完成后续销毁控件操作
        if self.user_bind_command:
            state = self.user_bind_command()
            # 如果某条件无法满足，中断销毁函数
            if state == 'break':
                return

        index = self.table_find(tab_id)

        # 如果关闭的是正在使用的面板，则将指向变量赋空
        if self.table_find(self.select_id) == index:
            self.select_id = None
        # 先删除窗口框架
        self.tabel_windows[index][0].destroy()
        self.tabel_windows[index][1].destroy()
        del self.tabel_windows[index]
        self._flush()

    def add(self, child, image_file=None, **kwargs):
        """添加一个面板"""

        table = NotBookTable(self.table_frame, image_file, **kwargs)
        table.shut_button.bind('<Button-1>', lambda event: self.shut_windows(table.frame))
        table.but.bind('<Button-1>', lambda event: self._flush(table.frame))

        self.tabel_windows.append((table.frame, child))
        self._flush(table.frame)

    def forget(self, tab_id):
        """为了兼容原本的api"""

        self.shut_windows(tab_id)

    def index(self, tab_id):
        """返回tab_id在表中的索引"""

        return self.table_find(tab_id)

    def select(self, tab_id=None):
        """如果焦点存在，则聚焦，否则返回当前指定的控件"""
        if not tab_id:
            return self.select_id

        self._flush(tab_id)

    def _flush(self, tab_id=None):
        """末尾刷新,只显示最后一个窗口"""

        # 如果没有指定id，直接刷新最后一个，如果表为空，则直接结束
        if not tab_id:
            if len(self.tabel_windows) == 0:
                return
            tab_id = self.tabel_windows[-1][0]

        # 指定index，方便索引和判断错误
        select_index = self.table_find(self.select_id)
        current_index = self.table_find(tab_id)
        if current_index is None:
            print(f"tab_id:{tab_id}, select_id:{self.select_id}")
            raise ValueError("table not have find's value")

        if self.select_id is not None:
            self.tabel_windows[select_index][1].pack_forget()
            self.tabel_windows[current_index][1].pack(fill=BOTH, expand=True)
            self.select_id = tab_id

        else:
            self.tabel_windows[current_index][1].pack(fill=BOTH, expand=True)
            self.select_id = tab_id


if __name__ == '__main__':
    root = Tk()
    nb = NotBook(root)

    frame1 = nb.get_frame()
    frame1.pack()
    Text(frame1).pack()
    nb.add(frame1, text="布局1", height=2, image_file=r"E:\IDE\resources\java.png")

    frame2 = nb.get_frame()
    frame2.pack()
    Button(frame2, text="这是布局二").pack()
    nb.add(frame2, text="布局2", height=2, image_file=r"E:\IDE\resources\python.png")

    nb.pack(fill=BOTH, expand=True)

    root.mainloop()



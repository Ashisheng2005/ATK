#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/1/17 下午6:57 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : ConvenienceMenu.py
# @desc : README.md

from tkinter import *


class ConvenienceMenu(Frame):
    """右击菜单"""

    def __init__(self, master, **kwargs):
        super().__init__(master=master)
        self.master = master
        self.menu = Menu(self.master, **kwargs)

    def add_cascade(self, **kwargs):
        """继承的方法"""

        self.menu.add_cascade(**kwargs)

    def add_command(self, **kwargs):
        """继承的方法"""

        self.menu.add_command(**kwargs)

    def add_separator(self):
        self.menu.add_separator()

    def show_menu(self, widget: Widget):
        """绑定"""

        def pout(event):
            self.menu.post(event.x + self.master.winfo_rootx(),
                           event.y + self.master.winfo_rooty())
            self.master.update()

        widget.bind('<Button-3>', pout)


if __name__ == '__main__':
    demo = Tk()
    label = Label(text="you can Right click")
    label.pack()

    menu = ConvenienceMenu(demo)
    menu.add_cascade(label='one')
    menu.add_cascade(label='tow')
    menu.show_menu(label)
    demo.mainloop()

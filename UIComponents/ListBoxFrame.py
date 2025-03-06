#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/2/27 下午10:00 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : ListBoxFrame.py
# @desc : README.md
from tkinter import *


class ListBoxFrame(Frame):

    def __init__(self, master):
        super().__init__(master=master)

        self.root_frame = Frame(self)
        self.root_frame.pack()

    def item_frame(self, text=None, path=None, image=None):
        """对于列表每一项的布局"""
        frame_root = Frame(self.root_frame)
        image_frame = Frame(frame_root)
        text_frame = Frame(frame_root)

        image_frame.pack(side=LEFT)
        text_frame.pack()

        if image:
            image = PhotoImage(file=image)
            image_label = Label(image_frame, image=image)
            image_label.image = image
            image_label.pack()

        if text:
            Label(text_frame, text=text, font=("黑体", 12)).pack(anchor=W)

        if path:
            Label(text_frame, text=path, font=("黑体", 10)).pack()

        # frame_root.bind("<Enter>")
        frame_root.pack()


if __name__ == '__main__':
    from UIComponents.NotBook import NotBook
    root = Tk()
    root.title("新建项目")
    not_book = NotBook(root)

    mix_project = not_book.get_frame()
    mix_project.pack()




    root.mainloop()



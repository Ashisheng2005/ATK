#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/2/12 下午8:16 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : ReceiverText.py
# @desc : README.md

from tkinter import *
from tkinter.scrolledtext import ScrolledText


class ReceiverText(Frame):

    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)

        self.receiver_text = ScrolledText(self.master, height=15, fg='#FFFFFF', bg="#3c3f41", font=("consolas", 11))

        # 默认模式为只读
        # self.receiver_text['state'] = "disabled"
        # 绑定回车，当触发回车的时候，获取改行内容，即为input输入内容
        # self.receiver_text.bind('<Return>', self.get_input_data)
        self.receiver_text.bind('<Key>', self.user_input)

        # 用来存放用户输入内容
        self.receiver_input_list = []
        # 换行后需要剔除的前缀
        self.prefixes = ""

        self.placement()

    def receiver_insert(self, index, chars, *args):
        """接受输出流"""

        # self.receiver_text['state'] = "normal"
        self.receiver_text.insert(index, chars, *args)
        # self.receiver_text['state'] = "disabled"
        # 自动滚动到最后一行
        self.receiver_text.see('end')
        return

    def get_line_text(self):
        row, column = self.receiver_text.index('insert').split('.')
        text = self.receiver_text.get(row + ".0", 'end')
        return text

    def user_input(self, event):

        if not self.prefixes:
            self.prefixes = self.get_line_text()

        # windows 和 linux 下可能不同，13 36
        if event.keycode == 13:
            text = self.get_line_text()
            self.receiver_input_list.append(text.strip(self.prefixes + '\n'))
            self.prefixes = ""
            print(self.receiver_input_list)

    def get_input_data(self, event):
        row, column = self.receiver_text.index('insert').split('.')
        text = self.receiver_text.get(row+".0", f'{row}.{column}')
        self.receiver_input_list = text.strip()

    def receiver_input(self, *args):
        """触发输入流"""
        # self.receiver_text['state'] = "normal"
        self.receiver_text.see('end')
        while True:
            if self.receiver_input_list:
                data = self.receiver_input_list
                self.receiver_input_list = ""
                # self.receiver_text['state'] = "disabled"
                return data

    def clear_text(self, index1='0.0', index2='end'):
        # 清空text内容

        self.receiver_text.delete(index1, index2)

    def placement(self):
        self.receiver_text.pack(fill=BOTH, expand=True)


if __name__ == '__main__':
    root = Tk()
    ReceiverText(root)
    root.mainloop()


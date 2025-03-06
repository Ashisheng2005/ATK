#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/1/16 下午8:37 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : DirectoryTree.py
# @desc : README.md
import os.path
# try:
#     from tkinter import Frame, LEFT, Y, END, Tk, Scrollbar, RIGHT
#     from tkinter import ttk
#     from os.path import basename, join, isdir
#     from os import listdir
#
#     from sys import path as sys_path
#     sys_path.append("..")
#     from Function import UIFunction
#
# except Exception as error:
#     print(error)

from os import listdir
# from pathlib import Path
from os.path import basename, join, isdir
from tkinter import Frame, LEFT, Y, END, Tk, Scrollbar, RIGHT, Menu, StringVar
from tkinter import ttk
from UIComponents.ConvenienceMenu import ConvenienceMenu


class DirectoryTree(Frame):
    """树状目录"""

    def __init__(self, master, path):
        super().__init__(master=master)
        self.master = master
        path = str(path)
        self.path = path
        # 树状组件初始化
        self.tree = ttk.Treeview(master)
        self.tree.pack(side=LEFT, fill=Y)
        tmp_path = path.replace('\\', '-')
        # 首先建造一个根节点并插入树状目录中
        root = self.tree.insert('', END,
                                text=basename(path),
                                open=True,
                                values=(tmp_path,))

        # 递归开始
        self._load_tree(root, path)

        # 可创建的文件类型
        self.file_type_True = ['.py', '.c', ".asm", '.jar']

        # 滚动条
        y_scrollbar = Scrollbar(self.master)
        y_scrollbar.pack(side=RIGHT, fill=Y)
        y_scrollbar.config(command=self.tree.yview)

        self.tree.config(yscrollcommand=y_scrollbar.set)

        # 用户选中的项目,用作刷新的时候标记
        self.user_select_item = StringVar()
        # 挂在右击菜单栏
        self.tree.bind('<Button-3>', self.show_menu)

        self.refresh()

    def refresh(self):
        # self.tree.delete('')
        for item in self.tree.get_children():
            self.tree.delete(item)

        tmp_path = self.path.replace('\\', '-')
        root = self.tree.insert('', END,
                                text=basename(str(self.path)),
                                open=True,
                                values=(tmp_path,))

        # 递归开始
        self._load_tree(root, self.path)
        # print('refresh')

        self.tree.update()
        self.tree.after(10000, self.refresh)

    def show_menu(self, event):
        menu_widget = self.menu(event)
        menu_widget.post(event.x + self.master.winfo_rootx(),
                       event.y + self.master.winfo_rooty())
        self.master.update()

    def menu(self, event):

        # 新建子菜单
        new_file_menu = Menu(self.master, tearoff=False)
        new_file_menu.add_command(label='文件')
        new_file_menu.add_command(label='目录')
        new_file_menu.add_separator()
        # 根据列表内容动态变更菜单
        for _ in self.file_type_True:
            new_file_menu.add_command(label=f'{_} 文件', command=lambda i=_: self.create_file(event, i))

        # 右击菜单栏
        tree_menu = Menu(self.master, tearoff=False)
        tree_menu.add_cascade(label='新建', accelerator='Ctrl+N', menu=new_file_menu)
        tree_menu.add_command(label='删除', accelerator='Delete')

        tree_menu.add_command(label='粘贴', accelerator='Ctrl+V')
        tree_menu.add_command(label='回滚', accelerator='Ctrl+H')
        tree_menu.add_command(label='重构', accelerator='Ctrl+R')
        tree_menu.add_separator()
        tree_menu.add_command(label='运行', accelerator='Ctrl+Shift+F10')
        tree_menu.add_command(label='调试', accelerator='Ctrl+D')

        return tree_menu

    def create_file(self, event, file_type):
        """根据file_type创建文件"""

        path = self.select_file(event)
        if not path:
            return

        if os.path.isdir(path):
            pass

        print(file_type)

    def select_file(self, event):
        """选中项目时候触发事件"""

        file_names = event.widget.selection()
        for item in file_names:
            # 文件名
            # file_name = self.tree.item(item)['text']
            # 文件或文件夹路径
            file_path = self.tree.item(item)['values'][0].replace('-', '\\')
            # print(file_name, file_path)

            return file_path

    def _load_tree(self, parent, parent_path):
        """通过递归的方式来排列出每个文件夹内容"""

        for file_name in listdir(parent_path):
            abs_path = join(parent_path, file_name)
            tmp_path = abs_path.replace('\\', '-')
            tree = self.tree.insert(parent, END,
                                    text=basename(abs_path),
                                    values=(tmp_path,))

            # 如果是文件夹，继续递归
            if isdir(abs_path):
                self._load_tree(tree, abs_path)


if __name__ == '__main__':
    demo = Tk()
    DirectoryTree(demo, path=r'E:\IDE')
    demo.mainloop()

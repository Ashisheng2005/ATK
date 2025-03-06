#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/1/21 下午6:19 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : ReplaceAndSearch.py
# @desc : README.md

from tkinter import *
from tkinter import messagebox
import re

# from sys import path as sys_path
# from Function.UIFunction import UIFunction
from UIComponents.RoundedCornerButton import RoundedButton


class FindSubstitutionFrame(Frame):
    """查找和替换的Frame, 默认替换Frame是隐藏的"""

    def __init__(self, master, *args, text_widget=None, shut_down_command=None, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        # 被查找数据
        self.text_widget = text_widget
        self.shut_down_command = shut_down_command
        self.text_widget.tag_configure("search_highlight", background="yellow")

        # 初始化变量
        self.matches = []
        self.current_match = 0

        self.find_frame = Frame(self.master)

        # 查找替换切换按钮
        self.open_substitution = RoundedButton(self.find_frame, text=">", radius=30,
                                               width=30, height=30, command=self.show_replace_frame)
        # 模式输入框
        self.parameters_enter = Text(self.find_frame, relief=FLAT, height=1, font=("黑体", 12))
        # 区分大小写
        self.case = RoundedButton(self.find_frame, text="Cc", radius=30, width=30, height=30)
        # 正则表达式
        self.Regular = RoundedButton(self.find_frame, text=".*", radius=30, width=30, height=30)
        # 上一个
        self.Up_last = RoundedButton(self.find_frame, text="↑", radius=30,
                                     width=30, height=30, select_foreground='#FFFFFF',
                                     command=lambda: self.find_next(growth=-1)
                                     )
        # 下一个
        self.Down_last = RoundedButton(self.find_frame, text="↓", radius=30,
                                       width=30, height=30, select_foreground='#FFFFFF', command=self.find_next)

        self.shout_down = RoundedButton(self.find_frame, text=" X ", radius=30,
                                       width=30, height=30, select_foreground='#FFFFFF', command=self.down)
        # 替换Frame
        self.replace_frame = Frame(self.master)
        # 模式输入框
        self.replace_enter = Text(self.replace_frame, relief=FLAT, height=1, font=("黑体", 12))

        self.replace_button = RoundedButton(
            self.replace_frame,
            text="替换",
            radius=30,
            width=80,
            height=20,
            select_foreground='#FFFFFF',
            font=("黑体", 10),
            command=self._replace
        )

        self.replace_all_button = RoundedButton(
            self.replace_frame,
            text="替换全部",
            radius=30,
            width=80,
            height=20,
            select_foreground='#FFFFFF',
            font=("黑体", 10),
            command=self._replace_all
        )

        # 放置控件
        self.placement()

    def show_replace_frame(self):
        if self.open_substitution.value:
            self.replace_frame.pack(fill=BOTH, expand=True)

        else:
            self.replace_frame.pack_forget()

    def down(self):
        self.replace_enter.delete("1.0", END)
        self.parameters_enter.delete('1.0', END)
        self.shut_down_command()

    def placement(self):
        self.open_substitution.pack(side=LEFT)
        self.parameters_enter.pack(side=LEFT, fill=X, expand=True)
        self.case.pack(side=LEFT)
        self.Regular.pack(side=LEFT)
        self.Up_last.pack(side=LEFT)
        self.Down_last.pack(side=LEFT)
        self.shout_down.pack()
        self.find_frame.pack(fill=BOTH, expand=True)

        self.replace_enter.pack(side=LEFT, fill=X, expand=True)
        self.replace_button.pack(side=LEFT)
        self.replace_all_button.pack(side=LEFT)

    def _compile_pattern(self):
        """编译正则表达式模式"""

        pattern = self.parameters_enter.get('1.0', END).strip("\n")

        # 判断是否选择正则匹配方式
        if not self.Regular.value:
            pattern = re.escape(pattern)  # 转义特殊字符（普通文本模式）

        return pattern

    def _get_matches(self):
        """获取所有匹配项的位置"""

        # 获取匹配字符
        content = self.text_widget.get('1.0', END)

        pattern = self._compile_pattern()
        flags = re.IGNORECASE if not self.case.value else 0
        matches = []
        for match in re.finditer(pattern, content, flags=flags):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            matches.append((start, end))
        return matches

    def _search(self):
        """搜索并存储匹配项"""

        self.matches = self._get_matches()
        if not self.matches:
            print(self.text_widget.get("1.0", END))
            messagebox.showinfo("提示", "未找到匹配项")
            self.current_match = 0

    def find_next(self, growth=1):
        """查找下一个, 先tag一个全局显示，然后在显示当前指向的某个"""

        # 完成搜索动作，并存储
        self._search()

        if self.matches:
            start, end = self.matches[self.current_match]
            # 清除上次痕迹
            self.text_widget.tag_remove("search_highlight", "1.0", END)
            # 重新渲染
            self.text_widget.tag_add("search_highlight", start, end)
            # 焦点追踪
            self.text_widget.see(start)

            # 越界处理
            self.current_match += growth
            if self.current_match >= 0:
                self.current_match = self.current_match % len(self.matches)

            else:
                self.current_match = len(self.matches) - 1

    def draw(self):
        """单纯刷新tag"""
        if self.matches:
            start, end = self.matches[self.current_match]
            # 清除上次痕迹
            self.text_widget.tag_remove("search_highlight", "1.0", END)
            # 重新渲染
            self.text_widget.tag_add("search_highlight", start, end)
            # 焦点追踪
            self.text_widget.see(start)

        # self.text_widget.tag_configure("search_highlight", background="yellow")

    def _replace(self):
        """替换当前匹配项"""
        if not self.matches:
            return
        start, end = self.matches[self.current_match]
        self.text_widget.delete(start, end)
        self.text_widget.insert(start, self.replace_enter.get("1.0", END).strip("\n "))
        self.matches = self._get_matches()  # 重新计算匹配项
        self.text_widget.tag_remove("search_highlight", "1.0", END)

    def _replace_all(self):
        """全部替换"""
        if not self.matches:
            return
        self.text_widget.tag_remove("search_highlight", "1.0", END)
        content = self.text_widget.get("1.0", END)
        flags = re.IGNORECASE if not self.case.value else 0
        pattern = self._compile_pattern()
        new_content = re.sub(pattern, self.replace_enter.get(1.0, END).strip("\n "), content, flags=flags)
        self.text_widget.delete("1.0", END)
        self.text_widget.insert("1.0", new_content)


if __name__ == '__main__':
    demo = Tk()
    text = Text(demo)
    text.pack()
    # text.tag_configure("search_highlight", background="yellow")
    frame2 = FindSubstitutionFrame(demo, text_widget=text)
    frame2.pack()
    demo.mainloop()

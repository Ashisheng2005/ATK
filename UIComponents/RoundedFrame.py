#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/2/27 下午9:37 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : RoundedFrame.py
# @desc : README.md

from tkinter import *


class RoundedFrame(Canvas, Frame):

    def __init__(self, master, radius=25, padding=10, background="#FFFFFF", **kwargs):
        Frame.__init__(self, master, **kwargs)
        # 圆角弧度
        self.radius = radius
        self.padding = padding
        self.background = background
        self.canvas_frame = Frame(self)

        self.canvas = Canvas(self.canvas_frame)
        self.canvas.pack(fill=BOTH, expand=True)





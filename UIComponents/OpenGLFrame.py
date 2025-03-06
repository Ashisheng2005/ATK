#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/1/17 下午7:53 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : OpenGLFrame.py
# @desc : README.md
# 已移植至plugins模块 2025.1.30

import os.path

from OpenGL.GL import *
from pyopengltk import OpenGLFrame
from pyautogui import position
from os import path

import live2d.v3 as live2d


class MyOpenGLFrame(OpenGLFrame):
    
    def __init__(self, *args, **kwargs):

        self.live2d_model_path = kwargs.get("model_path", False)
        if "model_path" in kwargs:
            del kwargs['model_path']

        OpenGLFrame.__init__(self, *args, **kwargs)
        # 相对路劲调整
        parent_path = os.path.abspath(os.path.join(os.path.dirname("__file__"), os.path.pardir))
        # 构建到live2d下的相对路劲
        self.live2d_dir = path.join(parent_path, 'live2d')
        # 识别live2d的模型路径
        if not self.live2d_model_path:
            self.live2d_dir_join(r"米塔\\3.model3.json")

        else:
            self.live2d_dir_join(self.live2d_model_path)

        self.global_coordinates = True
        self.MAPP = round(200 / 980, 2)
        self.model = None

    @classmethod
    def on_start_callback(cls, group: str, no: int):
        """动作开始触发事件"""
        
        print(f"touched and motion [{group}_{no}] is started")

    @classmethod
    def on_finish_callback(cls):
        """动作结束调用函数"""
        
        print("motion finished")

    @classmethod
    def end(cls):
        """结束之后的资源释放事件"""

        live2d.dispose()

    def touch(self):
        """被点击事件"""

        print("被点击")
        x, y = 100, 100
        self.model.Touch(x, y, self.on_start_callback, self.on_finish_callback)
        self.model.StartMotion("LipSync", 0, live2d.MotionPriority.FORCE)

    def live2d_dir_join(self, model_path):
        """模型路径的更新"""

        self.live2d_model_path = path.join(self.live2d_dir, model_path)

    def coordinate_compression(self):
        """坐标压缩函数，将UI内，live2dframe外的坐标压缩为frame内地映射坐标"""

        screen_x, screen_y = position()
        # x = screen_x - self.winfo_rootx()
        y = screen_y - self.winfo_rooty()

        if y > 160:
            y *= 0.2

    def initgl(self):
        """初始化"""

        self.animate = 1
        # self.after(100, self.printContext)
        # live2D初始化
        live2d.init()
        live2d.setLogEnable(False)
        live2d.glewInit()
        # glViewport(0, 0, self.width, self.height)
        # glClearColor(0.0, 1.0, 0.0, 0.0)

        self.model = live2d.LAppModel()
        if live2d.LIVE2D_VERSION == 2:
            # self.model.LoadModelJson(r"..\live2d\UG\ugofficial.model3.json")
            print(self.live2d_model_path)
            self.model.LoadModelJson(self.live2d_model_path)

        else:
            self.model.LoadModelJson(self.live2d_model_path)

        self.model.Resize(self.width, self.height)

    def _live2d_(self):
        """live2d模型的相关设置"""

        screen_x, screen_y = position()
        x = screen_x - self.winfo_rootx()
        y = screen_y - self.winfo_rooty()
        # sleep(0.02)
        live2d.clearBuffer()
        self.model.Update()
        self.model.Drag(x, y)
        self.model.Draw()

    def redraw(self):
        """重绘，刷新时调用"""

        glClear(GL_COLOR_BUFFER_BIT)
        self._live2d_()


if __name__ == '__main__':
    from tkinter import Tk, Frame
    demo = Tk()
    frame = Frame(demo)
    frame.pack()
    live2dFrame = MyOpenGLFrame(frame, width=1000, height=1000)
    live2dFrame.pack()
    demo.mainloop()


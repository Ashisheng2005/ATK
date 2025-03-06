#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/1/26 下午9:08 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : RoundedCornerButton.py
# @desc : README.md

import tkinter as tk


def lighten_color(hex_color, amount):
    # 将十六进制颜色转换为RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # 增加亮度
    new_rgb = tuple(min(255, int(c + amount)) for c in rgb)

    # 将RGB转换回十六进制颜色
    new_hex_color = '#{:02x}{:02x}{:02x}'.format(*new_rgb)
    return new_hex_color


class RoundedButton(tk.Canvas):
    """基于Canvas实现的圆角按钮"""

    def __init__(self, master, text="", radius=25, padding=10, command=None,
                 fore_ground='#FFFFFF', select_foreground='#2f5496', font=None, **kwargs):
        tk.Canvas.__init__(self, master, **kwargs)
        self.text = text
        self.radius = radius
        self.padding = padding
        self.command = command
        self.foreground = fore_ground
        self.font = font
        self.select_foreground = select_foreground
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.mouse_enter)
        self.bind("<Leave>", self.mouse_leave)
        # 按钮是否选中，value 1:True; 0:False
        self.value = 0
        # 按钮后续的操作对象初始化
        self.Button = None
        # 开始绘画
        self.draw(self.foreground)

    def mouse_enter(self, event):
        """鼠标进入动画效果"""
        amount = 50
        if self.foreground == self.select_foreground or not self.value:
            amount *= -1

        # 在原有色彩的基础上变化50
        self.draw(fill=lighten_color(
            self.foreground if not self.value else self.select_foreground,
            amount
            )
        )

    def bbox(self, *args):
        return self.master.bbox(*args)

    def mouse_leave(self, event):
        """如果按钮状态未改变，则还原前景色"""

        if not self.value:
            self.draw(fill=self.foreground)

        else:
            self.draw(fill=self.select_foreground)

    def draw(self, fill):
        # Calculate the width and height of the button
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        # fill = fill if not self.foreground else self.foreground

        # Create a rounded rectangle
        self.create_rounded_rectangle(0, 0, width, height, radius=self.radius, fill=fill)

        # Add text to the button
        self.create_text(
            width / 2,
            height / 2,
            text=self.text,
            font=self.font if self.font else ("Helvetica", 12)
        )

    def on_click(self, event):
        """"""

        self.value = 1 if not self.value else 0
        if self.value:
            self.draw(fill=self.select_foreground)

        if self.command:
            self.command()

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)


if __name__ == "__main__":
    def on_click():
        print("Button clicked!")

    root = tk.Tk()
    root.geometry("300x200")
    btn = RoundedButton(root, text="Click Me", radius=50, width=100, height=40, command=on_click)
    btn.pack()
    root.mainloop()


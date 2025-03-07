#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/3/6 下午9:33 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : __init__.py.py
# @desc : README.md

__all__ = []

import re
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import _flatten, _join, _stringify, _splitdict


def _format_optvalue(value, script=False):
    """Internal function."""
    if script:
        # if caller passes a Tcl script to tk.call, all the values need to
        # be grouped into words (arguments to a command in Tcl dialect)
        value = _stringify(value)
    elif isinstance(value, (list, tuple)):
        value = _join(value)
    return value


def _format_optdict(optdict, script=False, ignore=None):
    """Formats optdict to a tuple to pass it to tk.call.

    E.g. (script=False):
      {'foreground': 'blue', 'padding': [1, 2, 3, 4]} returns:
      ('-foreground', 'blue', '-padding', '1 2 3 4')"""

    opts = []
    for opt, value in optdict.items():
        if not ignore or opt not in ignore:
            opts.append("-%s" % opt)
            if value is not None:
                opts.append(_format_optvalue(value, script))

    return _flatten(opts)


def lighten_color(hex_color, amount):
    # 将十六进制颜色转换为RGB
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # 增加亮度
    new_rgb = tuple(min(255, int(c + amount)) for c in rgb)

    # 将RGB转换回十六进制颜色
    new_hex_color = '#{:02x}{:02x}{:02x}'.format(*new_rgb)
    return new_hex_color


def count(text1:str, text2:str, model) -> int:
    if model == 'start':
        return len(text1) - len(text1.lstrip(text2))

    return len(text1) - len(text1.strip(text2))


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
        """当按钮被点击的时候"""

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


class FindSubstitutionFrame(tk.Frame):
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

        self.find_frame = tk.Frame(self)

        # 查找替换切换按钮
        self.open_substitution = RoundedButton(self.find_frame, text=">", radius=30,
                                               width=30, height=30, command=self.show_replace_frame)
        # 模式输入框
        self.parameters_enter = tk.Text(self.find_frame, relief=tk.FLAT, height=1, font=("黑体", 12))
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
        self.replace_frame = tk.Frame(self.master)
        # 模式输入框
        self.replace_enter = tk.Text(self.replace_frame, relief=tk.FLAT, height=1, font=("黑体", 12))

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
            self.replace_frame.pack(fill=tk.BOTH, expand=True)

        else:
            self.replace_frame.pack_forget()

    def down(self):
        self.replace_enter.delete("1.0", tk.END)
        self.parameters_enter.delete('1.0', tk.END)
        self.shut_down_command()

    def placement(self):
        self.open_substitution.pack(side=tk.LEFT)
        self.parameters_enter.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.case.pack(side=tk.LEFT)
        self.Regular.pack(side=tk.LEFT)
        self.Up_last.pack(side=tk.LEFT)
        self.Down_last.pack(side=tk.LEFT)
        self.shout_down.pack()
        self.find_frame.pack(fill=tk.BOTH, expand=True)

        self.replace_enter.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.replace_button.pack(side=tk.LEFT)
        self.replace_all_button.pack(side=tk.LEFT)

    def _compile_pattern(self):
        """编译正则表达式模式"""

        pattern = self.parameters_enter.get('1.0', tk.END).strip("\n")

        # 判断是否选择正则匹配方式
        if not self.Regular.value:
            pattern = re.escape(pattern)  # 转义特殊字符（普通文本模式）

        return pattern

    def _get_matches(self):
        """获取所有匹配项的位置"""

        # 获取匹配字符
        content = self.text_widget.get('1.0', tk.END)

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
            print(self.text_widget.get("1.0", tk.END))
            messagebox.showinfo("提示", "未找到匹配项")
            self.current_match = 0

    def find_next(self, growth=1):
        """查找下一个, 先tag一个全局显示，然后在显示当前指向的某个"""

        # 完成搜索动作，并存储
        self._search()

        if self.matches:
            start, end = self.matches[self.current_match]
            # 清除上次痕迹
            self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
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
            self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
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
        self.text_widget.insert(start, self.replace_enter.get("1.0", tk.END).strip("\n "))
        self.matches = self._get_matches()  # 重新计算匹配项
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)

    def _replace_all(self):
        """全部替换"""
        if not self.matches:
            return
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        content = self.text_widget.get("1.0", tk.END)
        flags = re.IGNORECASE if not self.case.value else 0
        pattern = self._compile_pattern()
        new_content = re.sub(pattern, self.replace_enter.get(1.0, tk.END).strip("\n "), content, flags=flags)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", new_content)


class EditText(tk.Frame):
    """编辑框"""

    def __init__(self, master, file_name=None, reduced=False, font=None,
                 row_mark_fg='#FFFFFF', row_mark_bg='#000000', sele_line_fg="gray", sele_line_bg=None,
                 sele_row_mark_fg='gray', sele_row_mark_bg='white',sub_tab = True,
                 **kwargs):
        super().__init__(master)
        self.master = master

        # 打开的文件名
        self.text_file_name = file_name

        # 是否开启略缩图
        self.reduced_text = reduced

        # 对于同一个键盘事件定义若干个函数，启用冗余变量，为插件预留api
        self.key_release_command = None

        # edit的文字设置
        self.font = ["consolas", 12] if not font else font

        # 绑定x轴的滑动条
        self.x_scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.text_frame = tk.Frame(self)

        # 代码编辑框
        kwargs['font'] = self.font
        self.Text = ScrolledText(self.text_frame, **kwargs, wrap='none', undo=True)

        self.row_mark_fg = row_mark_fg
        self.row_mark_bg = row_mark_bg

        # 选中的行高光
        self.sele_line_fg = sele_line_fg
        self.sele_line_bg = sele_line_bg

        # 选中行标的高光
        self.sele_row_mark_fg = sele_row_mark_fg
        self.sele_row_mark_bg = sele_row_mark_bg

        # 替换Tab键
        self.sub_tab = sub_tab

        # 左侧行标框
        self.Row_mark = tk.Text(self, fg=self.row_mark_fg, bg=self.row_mark_bg, **kwargs)

        # 行标高亮是否可用
        self.Text.height_use = True

        if self.reduced_text:
            # 文本略缩图, 强制构建一个未初始化的tcl可以理解的空间层名称，详情见BaseWidget._setup
            self.peer = "!".join(self.Text.__str__().split("!")[:-1]) + "!peer"
            self.Text.peer_create(self.peer, borderwidth=0, relief='flat', font=("consolas", 1),
                                  height=160, insertbackground='#000000', insertborderwidth=1, wrap='char')

        # 初始化之后的属性绑定
        self._initialization()

    # def _forget_replace_find_frame(self):
    #     """隐藏查找组件"""
    #
    #     self.Text.tag_remove('search_highlight', "1.0", tk.END)
    #     self.Text.height_use = False
    #     self.find_replace_frame.pack_forget()

    # def _pack_replace_find_frame(self, event):
    #     """显示查找组件，并判断用户是否存在选中内容"""
    #
    #     if self.Text.height_use:
    #         self._forget_replace_find_frame()
    #
    #     try:
    #         start_index = self.Text.index(tk.SEL_FIRST)
    #         end_index = self.Text.index(tk.SEL_LAST)
    #         selected_text = self.Text.get(start_index, end_index)
    #         self.find_frame.parameters_enter.insert("1.0", selected_text)
    #         self.Text.tag_remove('line_highlight', "1.0", tk.END)
    #         self.Text.height_use = True
    #
    #     except Exception as error:
    #         pass
    #
    #     finally:
    #         self.find_replace_frame.pack(fill=tk.BOTH, expand=True)

    def _initialization(self):
        """控件初始化之后的绑定事件"""

        self.Row_mark.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        self.text_frame.pack()
        self.x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.Text.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT if self.reduced_text else tk.TOP)
        # self.find_frame.pack()
        self.x_scrollbar.config(command=self.Text.xview)
        self.Text.vbar.configure(command=self._scroll)
        self.Text.config(xscrollcommand=self.x_scrollbar.set)

        # 键盘鼠标事件绑定
        # 鼠标滚动事件
        self.Row_mark.bind("<MouseWheel>", self.wheel)
        self.Text.bind("<MouseWheel>", self.wheel)
        self.Text.bind("<Control-MouseWheel>", self.set_font_size)

        # 键盘方向键事件
        self.Text.bind("<KeyPress-Up>", self.keypress_scroll)
        self.Text.bind("<KeyPress-Down>", self.keypress_scroll)
        self.Text.bind("<KeyPress-Left>", self.keypress_scroll)
        self.Text.bind("<KeyPress-Right>", self.keypress_scroll)

        # 文本选中事件
        self.Text.bind("<<Selection>>", self.on_selection)

        # 接管tab案件事件
        if self.sub_tab:
            self.Text.bind("<Tab>", self.tab_key_command)

        self.Text.bind("<KeyRelease>", self._key_release_command)

        # 光标所在行高亮追踪
        self.Text.bind('<ButtonRelease-1>', self.line_highlight_tracking)

        # 显示查找组件
        # self.Text.bind("<Control-f>", self._pack_replace_find_frame)

        if self.reduced_text:
            self.Text.tk.call('pack', self.peer, *(_format_optdict({"fill": tk.BOTH, "expand": True})))

        # 正常刷新
        self.show_line()

    def _key_release_command(self, event):
        self.return_key_release_command(event)
        self.get_txt(event)
        if self.key_release_command:
            self.key_release_command()

    def tab_key_command(self, event):
        # Tab事件
        self.Text.insert("insert", " " * 4)
        return 'break'

    def return_key_release_command(self, event):
        # 回车事件
        if event.keycode == 13:
            row, column = map(int, self.Text.index('insert').split("."))
            text = self.Text.get(f"{row - 1}.0", f"{row - 1}.end")
            spaces = count(text, " ", "start")
            text = text.strip()
            if len(text) > 0 and text[-1] == ":":
                spaces += 4

            self.Text.insert('insert', " " * spaces)

    def set_font_size(self, event):
        """根据鼠标滚轮改变字体大小"""

        # 滚轮一次触发delta返回 120（windows）或 -120
        if event.delta > 0:
            self.font[1] += 1

        else:
            self.font[1] -= 1

        # 刷新显示字体的大小
        self.Text['font'] = self.font
        self.Row_mark['font'] = self.font
        self.show_line()

    def line_highlight_tracking(self, event=None):
        """编辑行的高亮追踪"""

        if not self.Text.height_use:
            return

        # 先删除标签
        self.Text.tag_delete('line_highlight')
        self.Row_mark.tag_delete('line_highlight')

        # 获取光标所在行位置
        line_table = self.Text.index('insert')
        row, column = map(int, line_table.split("."))
        # 设置标签
        self.Text.tag_add('line_highlight', f"{row}.0", f"{row + 1}.0")
        self.Row_mark.tag_add('line_highlight', f"{row}.0", f"{row + 1}.0")

        self.Text.tag_config('line_highlight', background=self.sele_line_bg,
                             foreground=self.sele_line_fg if self.sele_line_fg else None)

        self.Row_mark.tag_config('line_highlight', background=self.sele_row_mark_bg, foreground=self.sele_row_mark_fg)
        self.Text.tag_configure("search_highlight", background="yellow")

    def insert(self, *args, **kwargs):
        """文本插入函数继承"""

        self.Text.insert(*args, **kwargs)
        # 标签刷新
        self.show_line()

    def delete(self, *args, **kwargs):
        """文本框内容删除"""

        self.Text.delete(*args, **kwargs)
        self.show_line()

    def get(self, *args, **kwargs):
        """获取文本框内容"""

        return self.Text.get(*args, **kwargs)

    def get_txt(self, event):
        """绑定的文本修改事件"""

        self.show_line()

    def on_selection(self, event):
        """文本选中事件, 确保触发事件之后，行标依然准确"""

        self.Row_mark.yview(tk.MOVETO, self.Text.vbar.get()[0])

    def keypress_scroll(self, event=None, moving=0, row=0):
        """对于键盘方向键的处理"""

        # 获取光标所在行和位置
        line, column = map(int, self.Text.index(tk.INSERT).split('.'))
        # 当前显示的范围最上层
        first_line = int(self.Text.index("@0,0").split('.')[0])
        # 当前显示的范围最下层
        end_line = int(self.Text.index("@0," + str(self.Text.winfo_height())).split('.')[0])

        # 光标超出显示范围时，先滚动平魔到光标能显示的区域
        if line <= first_line + row or line >= end_line - row:
            self.see_line(line)

        if row:
            return

        if event.keysym == "Up":
            # 键盘Up键
            if line <= first_line + 1:
                moving = -1

        elif event.keysym == "Down":
            # 键盘Down键
            if line >= end_line - 1:
                moving = 1

        elif event.keysym == "Left":
            # 键盘Left事件
            if line <= first_line + 1 and not column:
                moving = -1

        elif event.keysym == "Right":
            text = self.Text.get('1.0', tk.END)
            cursor_line = text.split("\n")[line - 1]
            line_length = len(cursor_line)
            if line >= end_line - 1 and column == line_length:
                moving = 1

        self.Row_mark.yview_scroll(moving, tk.UNITS)
        self.Text.yview_scroll(moving, tk.UNITS)

    def see_line(self, line):
        """按键滚动的框体相应事件"""

        self.Text.see(f"{line}.0")
        self.Row_mark.see(f"{line}.0")

    def wheel(self, event):
        """处理鼠标滚动事件, 根据鼠标滚动的距离，更新显示参数"""

        self.Row_mark.yview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)
        self.Text.yview_scroll(int(-1 * (event.delta / 120)), tk.UNITS)
        # 截断句柄
        return 'break'

    def _scroll(self, *xy):
        """处理滚动条滚动事件, 同步垂直滚动位置"""

        self.Text.yview(*xy)
        self.Row_mark.yview(*xy)

    def show_line(self):
        """刷新事件"""

        # 获取文本行数
        text_lines = int(self.Text.index('end-1c').split('.')[0])
        # 计算行数最多有多少行，进行微调
        len_lines = len(str(text_lines))
        self.Row_mark['width'] = len_lines + 2

        # 将显示行数文本的状态设置为正常
        self.Row_mark.configure(state=tk.NORMAL)
        # 删除文本中的所有内容
        self.Row_mark.delete('1.0', 'end')

        # 遍历添加行标
        for i in range(1, text_lines + 1):
            if i == 1:
                self.Row_mark.insert(tk.END, " " * (len_lines - len(str(i)) + 1) + str(i))

            else:
                self.Row_mark.insert(tk.END, "\n" + " " * (len_lines - len(str(i)) + 1) + str(i))

        # 因为滑动条导致的空白，多加一行空白填充再行标上
        self.Row_mark.insert(tk.END, "\n")

        # 模拟滚动条滚动
        self._scroll(tk.MOVETO, self.Text.vbar.get()[0])
        # 将文本状态修改为禁用
        self.Row_mark.configure(state=tk.DISABLED)
        # 处理光标超出范围情况，否则行数不会同步
        self.keypress_scroll(row=1)
        # 行追踪刷新
        self.line_highlight_tracking()
        # 刷新
        self.master.update()


class NotBookTable:

    def __init__(self, master=None, image_file=None, **kwargs):
        self.master = master
        self.kw = kwargs

        # 关于选中的状态
        self.select_state = True
        self.frame = tk.Frame(self.master)
        self.shut_button = None
        self.but = None
        self.create_but(image_file)

    def create_but(self, image=None):
        if image:
            image = tk.PhotoImage(file=image)
            photo = tk.Label(self.frame, image=image, text="  ", compound='right')
            photo.image = image
            photo.pack(side=tk.LEFT)

        self.but = tk.Label(self.frame, **self.kw)
        self.but.pack(side=tk.LEFT)
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

        self.frame.pack(side=tk.LEFT)
        return self.but


class NotBook(tk.Frame):

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
        self.table_frame = tk.Frame(self)
        # 下方的窗口框架
        self.windows_frame = tk.Frame(self)
        # 外部定义的方法
        self.user_bind_command = None
        self.placement()

    def placement(self):
        self.table_frame.pack(side=tk.TOP, fill=tk.X)
        self.windows_frame.pack(fill=tk.BOTH, expand=True)

    def get_frame(self):
        """注册一个页面，外部像内部申请一个frame"""
        frame = tk.Frame(self.windows_frame)
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
            self.tabel_windows[current_index][1].pack(fill=tk.BOTH, expand=True)
            self.select_id = tab_id

        else:
            self.tabel_windows[current_index][1].pack(fill=tk.BOTH, expand=True)
            self.select_id = tab_id


class ToolTip:
    """控件注释标签"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """鼠标进入控件范围执行函数"""

        # 首相执行控件自带的动画
        self.widget.mouse_enter(event)

        # 获取绝对位置
        x, y, _, _ = self.widget.bbox("insert")

        # 设置偏移量
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        """鼠标离开控件范围执行函数"""

        # 首相执行控件自带的动画
        self.widget.mouse_leave(event)

        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None


if __name__ == '__main__':
    demo = tk.Tk()

    notbook = NotBook(demo)
    frame_1 = notbook.get_frame()
    EditText(frame_1).pack()
    notbook.add(frame_1, text="asd")
    notbook.pack()
    demo.mainloop()

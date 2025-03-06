#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2025/1/16 上午11:44 
# @Author : Huzhaojun
# @Version：V 1.0
# @File : EditText.py
# @desc : README.md

from tkinter import *
from tkinter import SEL_FIRST, SEL_LAST
from tkinter import _flatten, _join, _stringify, _splitdict
from tkinter.scrolledtext import ScrolledText
from UIComponents.ReplaceAndSearch import FindSubstitutionFrame


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



class EditText(Frame):
    """编辑框"""

    def __init__(self, master, file_name=None, **kwargs):
        super().__init__(master)
        self.master = master
        # 打开的文件名
        self.text_file_name = file_name
        # 对于同一个键盘事件定义若干个函数，启用冗余变量，为插件预留api
        self.key_release_command = None

        # edit的文字设置
        self.font = ["consolas", 12]

        # 绑定x轴的滑动条
        self.x_scrollbar = Scrollbar(self.master, orient=HORIZONTAL)
        # 代码编辑框
        kwargs['font'] = self.font
        self.Text = ScrolledText(self.master, **kwargs, wrap='none', undo=True, fg='#FFFFFF', bg="#3c3f41")
        # 左侧行标框
        self.Row_mark = Text(self.master, fg='#FFFFFF', bg="#3c3f41",**kwargs)
        # 查找和替换的Frame
        self.find_replace_frame = Frame(self.master)
        self.find_frame = FindSubstitutionFrame(
            self.find_replace_frame,
            text_widget=self.Text,
            shut_down_command=self._forget_replace_find_frame
        )
        # 行标高亮是否可用
        self.Text.height_use = True

        # 文本略缩图, 强制构建一个未初始化的tcl可以理解的空间层名称，详情见BaseWidget._setup
        self.peer = "!".join(self.Text.__str__().split("!")[:-1]) + "!peer"

        self.Text.peer_create(self.peer, borderwidth=0, relief='flat', font=("consolas", 1), height=160,fg='#FFFFFF',
                              bg="#3c3f41", insertbackground='#000000', insertborderwidth=1, wrap='char')

        # 初始化之后的属性绑定
        self._initialization()

    def _forget_replace_find_frame(self):
        """隐藏查找组件"""

        self.Text.tag_remove('search_highlight', "1.0", END)
        self.Text.height_use = False
        self.find_replace_frame.pack_forget()

    def _pack_replace_find_frame(self, event):
        """显示查找组件，并判断用户是否存在选中内容"""

        if self.Text.height_use:
            self._forget_replace_find_frame()

        try:
            start_index = self.Text.index(SEL_FIRST)
            end_index = self.Text.index(SEL_LAST)
            selected_text = self.Text.get(start_index, end_index)
            self.find_frame.parameters_enter.insert("1.0", selected_text)
            self.Text.tag_remove('line_highlight', "1.0", END)
            self.Text.height_use = True

        except Exception as error:
            pass

        finally:
            self.find_replace_frame.pack(fill=BOTH, expand=True)

    def _initialization(self):
        """控件初始化之后的绑定事件"""

        self.Row_mark.pack(side=LEFT, expand=NO, fill=Y)

        self.x_scrollbar.pack(side=BOTTOM, fill=X)
        self.Text.pack(fill=BOTH, expand=YES, side=LEFT)

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
        # 文本框内容被修改时触发
        # self.Text.bind("<<TextModified>>", self.get_txt)
        # 接管tab案件事件
        self.Text.bind("<Tab>", self.tab_key_command)
        self.Text.bind("<KeyRelease>", self._key_release_command)

        # 光标所在行高亮追踪
        self.Text.bind('<ButtonRelease-1>', self.line_highlight_tracking)

        # 显示查找组件
        self.Text.bind("<Control-f>", self._pack_replace_find_frame)

        self.Text.tk.call('pack', self.peer, *(_format_optdict({"fill":BOTH, "expand":True})))

        # 正常刷新
        self.show_line()

    def _key_release_command(self, event):
        self.return_key_release_command(event)
        self.get_txt(event)
        self.key_release_command()

        # if len(self.key_release_command) > 0:
        #     for item in self.key_release_command:
        #         item()

        # self.get_txt(event)

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
            text = text.split()
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

        self.Text.tag_config('line_highlight', background="#000000")
        self.Row_mark.tag_config('line_highlight', background='gray', foreground='white')
        self.Text.tag_configure("search_highlight", background="yellow")

        # self.find_frame.draw()

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

        self.Row_mark.yview(MOVETO, self.Text.vbar.get()[0])

    def keypress_scroll(self, event=None, moving=0, row=0):
        """对于键盘方向键的处理"""

        # 获取光标所在行和位置
        line, column = map(int, self.Text.index(INSERT).split('.'))
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
            text = self.Text.get('1.0', END)
            cursor_line = text.split("\n")[line - 1]
            line_length = len(cursor_line)
            if line >= end_line - 1 and column == line_length:
                moving = 1

        self.Row_mark.yview_scroll(moving, UNITS)
        self.Text.yview_scroll(moving, UNITS)

    def see_line(self, line):
        """按键滚动的框体相应事件"""

        self.Text.see(f"{line}.0")
        self.Row_mark.see(f"{line}.0")

    def wheel(self, event):
        """处理鼠标滚动事件, 根据鼠标滚动的距离，更新显示参数"""

        self.Row_mark.yview_scroll(int(-1 * (event.delta / 120)), UNITS)
        self.Text.yview_scroll(int(-1 * (event.delta / 120)), UNITS)
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
        self.Row_mark.configure(state=NORMAL)
        # 删除文本中的所有内容
        self.Row_mark.delete('1.0', 'end')

        # 遍历添加行标
        for i in range(1, text_lines + 1):
            if i == 1:
                self.Row_mark.insert(END, " " * (len_lines - len(str(i)) + 1) + str(i))

            else:
                self.Row_mark.insert(END, "\n" + " " * (len_lines - len(str(i)) + 1) + str(i))

        # 因为滑动条导致的空白，多加一行空白填充再行标上
        self.Row_mark.insert(END, "\n")

        # 模拟滚动条滚动
        self._scroll(MOVETO, self.Text.vbar.get()[0])
        # 将文本状态修改为禁用
        self.Row_mark.configure(state=DISABLED)
        # 处理光标超出范围情况，否则行数不会同步
        self.keypress_scroll(row=1)
        # 行追踪刷新
        self.line_highlight_tracking()
        # 刷新
        self.master.update()


if __name__ == '__main__':
    demo = Tk()
    EditText(demo)
    demo.mainloop()


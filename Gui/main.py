from pathlib import Path
import pyautogui
from sys import argv
import threading
from time import sleep
from webbrowser import open as open_url
import wx

# 版本信息
__version__ = "2.0.0.4"
__author__ = "xystudio"

# 自定义的事件
ID_UPDATE = wx.NewIdRef()
ID_UPDATE_LOG = wx.NewIdRef()
ID_SUPPORT_AUTHOR = wx.NewIdRef()
ID_MORE_UPDATE_LOG = wx.NewIdRef()
ID_MOUSE_LEFT = wx.NewIdRef()
ID_MOUSE_RIGHT = wx.NewIdRef()

def get_resource_path(*paths):
    """
    获取资源文件路径
    """
    resource = Path(__file__).parent.resolve() / "res" # 获取当前目录的资源文件夹路径
    return str(resource.joinpath(*paths))

# 主窗口绘制和事件监听
class MainWindow(wx.Frame):
    def __init__(self, parent=None):
        # 初始化
        super().__init__(parent, title="ClickMouse", size=(400, 350))

        # 状态控制变量
        self.running = False
        self.paused = False
        self.click_thread = None

        # 窗口初始化
        self.Icon = wx.Icon(str(get_resource_path("icons", "icon.ico")), wx.BITMAP_TYPE_ICO)
        self.Title = "ClickMouse"

        # 创建面板
        panel = wx.Panel(self)
        panel.SetFocus()

        # 面板控件
        # 标题大字文本
        wx.StaticText(panel, -1, "鼠标连点器", wx.Point(115, 5), style=wx.ALIGN_CENTER).SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        # 定义按钮
        self.button_left = wx.Button(panel, label="左键连点", pos=wx.Point(5, 60), size=wx.Size(100, 50))
        self.button_right = wx.Button(panel, label="右键连点", pos=wx.Point(280, 60), size=wx.Size(100, 50))
        self.pause_button = wx.Button(panel, label="暂停", pos=wx.Point(137, 60), size=wx.Size(100, 40))
        self.stop_button = wx.Button(panel, label="停止", size=wx.Size(100, 40))

        # 定义输入延迟的输入框
        self.text_control_tip = wx.StaticText(panel, -1, "延迟(毫秒):", wx.Point(50, 250), style=wx.ALIGN_CENTER).SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.delay_input = wx.TextCtrl(panel, value="", pos=wx.Point(150, 245), size=wx.Size(200, 25))

        # 设置布局
        panel.SetSizer(self.create_sizer())

        # 创建菜单栏
        self.create_menu_bar()
        
        # 绑定事件
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_update, id=ID_UPDATE)
        self.Bind(wx.EVT_MENU, self.on_update_log, id=ID_UPDATE_LOG)
        self.button_left.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left)
        self.button_right.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_right)

    def on_exit(self, event):
        """退出程序"""
        self.Close()

    def on_about(self, event):
        """显示关于窗口"""
        about_dialog = AboutWindow(self)
        about_dialog.ShowModal()
        about_dialog.Destroy()

    def on_update(self, event):
        """检查更新"""
        open_url("https://github.com/xystudio/pyClickMouse/releases")
    
    def on_update_log(self, event):
        """显示更新日志"""
        update_window = UpdateWindow(self)
        update_window.ShowModal()
        update_window.Destroy()
    
    def on_mouse_left(self, event):
        # 停止当前运行的点击线程
        if self.click_thread and self.click_thread.is_alive():
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动左键点击
        delay = self.delay_input.GetValue()
        self.mouse_click(button="left", delay=delay)

    def on_mouse_right(self, event):
        # 停止当前运行的点击线程
        if self.click_thread and self.click_thread.is_alive():
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动右键点击
        delay = self.delay_input.GetValue()
        self.mouse_click(button="right", delay=delay)


    def create_contol_button(self, sizer: wx.BoxSizer, button: wx.Button):
        """创建控制按钮"""
        sizer.AddStretchSpacer()
        sizer.Add(button, 0, wx.ALL, 3)
        sizer.AddStretchSpacer()

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "退出(&X)")
        
        # 帮助菜单
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "关于(&A)")
        help_menu.Append(ID_UPDATE, "更新(&U)")
        help_menu.Append(ID_UPDATE_LOG, "更新日志(&L)")
        
        # 添加菜单到菜单栏
        menubar.Append(file_menu, "文件(&F)")
        menubar.Append(help_menu, "帮助(&H)")
        
        # 设置菜单栏
        self.SetMenuBar(menubar)

    def create_sizer(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL) # 主布局
        main_sizer.AddSpacer(50)

        # 按钮的布局
        # 第一行的布局
        sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h1.Add(self.button_left, 1, wx.EXPAND | wx.ALL, 5)
        sizer_h1.AddSpacer(150)
        sizer_h1.Add(self.button_right, 1, wx.EXPAND | wx.ALL, 5)

        # 第二行的布局
        sizer_h2 = wx.BoxSizer(wx.HORIZONTAL)

        self.create_contol_button(sizer_h2, self.pause_button)

        # 第三行的布局
        sizer_h3 = wx.BoxSizer(wx.HORIZONTAL)
        self.create_contol_button(sizer_h3, self.stop_button)

        # 添加行布局到主布局
        main_sizer.Add(sizer_h1, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sizer_h2, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sizer_h3, 0, wx.EXPAND | wx.ALL, 5)

        return main_sizer
    
    def mouse_click(self, button: str, delay: int):
        """鼠标连点"""
        # 重置状态
        if self.click_thread and self.click_thread.is_alive():
            self.running = False
            self.click_thread.join()

        # 运行状态控制
        self.running = True
        self.paused = False
        
        # 判断参数有效性
        try:
            delay = int(delay)
            if delay < 1:
                raise ValueError
        except ValueError:
            wx.MessageBox("请输入有效的正整数延迟", "错误", wx.ICON_ERROR)
            return

        # 创建独立线程避免阻塞GUI
        def click_loop():
            while self.running:
                if not self.paused:
                    try:
                        pyautogui.click(button=button)
                        wx.CallAfter(self.Update)  # 更新GUI
                        sleep(delay/1000)
                    except Exception as e:
                        wx.CallAfter(wx.MessageBox, 
                                f"发生错误: {str(e)}",
                                "错误", 
                                wx.ICON_ERROR)
                        break
                else:
                    sleep(0.1)  # 暂停时降低CPU占用
        
        def on_pause_click(event):
            self.paused = not self.paused
            if self.paused:
                self.pause_button.SetLabel("重启")
            else:
                self.pause_button.SetLabel("暂停")
            # 强制刷新按钮显示
            self.pause_button.Update()

        self.pause_button.Bind(wx.EVT_BUTTON, on_pause_click)

        # 启动线程
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()

        # 绑定控制按钮
        self.stop_button.Bind(wx.EVT_BUTTON, lambda e: setattr(self, 'running', False))
        self.stop_button.Bind(wx.EVT_BUTTON, lambda e: (
        setattr(self, 'running', False),
        self.pause_button.SetLabel("暂停")
    ))


class AboutWindow(wx.Dialog):
    def __init__(self, parent=MainWindow):
        super().__init__(parent, title="关于", size=(300, 200)) # 初始化

        # 创建面板
        panel = wx.Panel(self)

        # 面板控件
        image = wx.Image(str(get_resource_path("icons","icon.png")), wx.BITMAP_TYPE_PNG).ConvertToBitmap() # 加载图标

        # 绘制内容
        wx.StaticBitmap(panel, -1, image, wx.Point(0, 0))
        wx.StaticText(panel, -1, f"ClickMouse,版本{__version__}\n\n一款快捷，使用C++制作的鼠标连点器", wx.Point(64, 15))
        wx.StaticText(panel, -1, f"本软件完全开源，作者为xystudio。建议前往项目地址来个star！", wx.Point(5, 75), wx.Size(270, 50))
        
        # 按钮
        wx.Button(panel, wx.ID_OK, "确定", wx.Point(200, 130))
        wx.Button(panel, ID_SUPPORT_AUTHOR, "支持作者", wx.Point(0, 130))

        # 绑定事件
        self.Bind(wx.EVT_BUTTON, self.on_support_author, id=ID_SUPPORT_AUTHOR)

    def on_support_author(self, event):
        """支持作者"""
        open_url("https://github.com/xystudio/pyClickMouse")

class UpdateWindow(wx.Dialog):
    def __init__(self, parent=MainWindow):
        super().__init__(parent, title="更新日志", size=(300, 750))# 初始化

        point_y = 5 # 初始y坐标
        update_logs: dict[str, list[str, wx.Size]] = {
            "2025/08/03    v1.0.0.0" : ["ClickMouse上线", self.size()], 
            "2025/08/04    v1.1.0.0" : ["对'关于'界面更新：\n\t添加了\"支持作者\"按钮\n\t移动'更新按钮'到主窗口的'帮助'菜单\n添加了找不到焦点提示", self.size(70)],
            "2025/08/08    v1.1.2.0" : ["添加了“更新日志”界面", self.size()],
            "2025/08/12    v1.1.2.3" : ["修改了部分显示字符\n修复了当关闭\"更新日志\"时，主窗口一并关闭的问题", self.size(60)],
            "2025/08/21    v2.0.0.4" : ["使用python重构代码", self.size()],
        } # 将日志存储在字典中，方便管理

        # 创建面板
        panel = wx.Panel(self)

        # 动态加载ui
        # 通过字典存储的日志信息来绘制日志内容，并动态计算日志的高度，减少代码量且更加方便管理
        for k, v in update_logs.items():
            wx.StaticText(panel, -1, k, wx.Point(5, point_y), v[1])
            point_y += 15 # 动态计算下一个日志内容的y坐标
            wx.StaticText(panel, -1, v[0], wx.Point(5, point_y), v[1])
            point_y += v[1].height # 动态计算下一个日志日期信息的y坐标

        # 调整页面高度，适配现在的更新日志界面大小
        self.Size = (self.Size[0], point_y + 130)

        # 面板控件
        wx.StaticText(panel, -1,"最多显示5个更新日志，更多更新日志请查阅github releases.", wx.Point(5, point_y + 10), (self.size(40)))

        # 按钮
        wx.Button(panel, wx.ID_OK, "确定", wx.Point(200, point_y + 50))
        wx.Button(panel, ID_MORE_UPDATE_LOG, "更多日志", wx.Point(0, point_y + 50))
        # 绑定事件
        self.Bind(wx.EVT_BUTTON, self.on_more_update_log, id=ID_MORE_UPDATE_LOG)

    def on_more_update_log(self, event):
        """显示更多更新日志"""
        open_url("https://github.com/xystudio/pyClickMouse/releases")

    def size(self, height: int = 20) -> wx.Size:
        return wx.Size(270, height)

# 显示窗口
def main():
    app = wx.App()
    frame = MainWindow()
    frame.Show()
    app.MainLoop()

def command():
    """
    ClickMouse命令行工具的函数
    """
    print('ClickMouse命令行工具未实现，敬请期待')

if __name__ == '__main__':
    if argv[1:]:
        # 调用命令行工具
        command()
    else:
        # 调用GUI工具
        main()
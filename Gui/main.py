# 加载库
from pathlib import Path # 文件管理库
import pyautogui # 鼠标操作库
from sys import argv # 获取命令行参数
import threading # 用于鼠标点击
from time import sleep, time # 延迟
from webbrowser import open as open_url # 关于作者
import wx # GUI库
import version # 版本信息
import log # 日志系统
from check_update import check_update # 更新检查
from datetime import datetime # 用于检查缓存的时间和现在相差的时间
import json # 用于读取配置文件

# 定义数据路径
data_path = Path("data")
update_cache_path = data_path / "update.json"

# 创建文件夹（如果不存在）
data_path.mkdir(parents=True, exist_ok=True)

class ResultThread(threading.Thread):
    """带有返回值的线程"""
    def __init__(self, target, args=(), deamon=False):
        super().__init__()
        self.target = target
        self.args = args
        self.deamon = deamon
        self._result = None
    
    def run(self):
        self._result = self.target(*self.args)
        
    def result(self):
        return self._result
    
def load_update_cache():
    """
    加载更新缓存文件
    """
    log.info("加载缓存文件")
    if update_cache_path.exists():
        with open(update_cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
        return cache
    else:
        # 创建文件
        with open(update_cache_path, "w", encoding="utf-8") as f:
            f.write("{}")
            return {}
        
def save_update_cache(**kwargs):
    """写入更新缓存文件"""
    log.info("写入缓存文件")
    cache_data = {
        "last_check_time": time(),
        **kwargs
    }
    with open(update_cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)
        
def should_check_update():
    """
    检查是否应该检查更新
    """
    log.info("检查是否应该检查更新")
    last_check_time = load_update_cache().get("last_check_time")
    if not last_check_time:
        return True
    last_check_time_stamp = datetime.fromtimestamp(last_check_time)
    now = datetime.now()
    if (now - last_check_time_stamp).total_seconds() > 3600 * 24:
        return True
    return False

log.info("加载库成功")

# 版本信息
__version__ = version.get_version()
__author__ = "xystudio"

# 自定义的事件
ID_UPDATE = wx.NewIdRef()
ID_UPDATE_LOG = wx.NewIdRef()
ID_SUPPORT_AUTHOR = wx.NewIdRef()
ID_MORE_UPDATE_LOG = wx.NewIdRef()
ID_MOUSE_LEFT = wx.NewIdRef()
ID_MOUSE_RIGHT = wx.NewIdRef()
ID_CLEAN_LOG = wx.NewIdRef()

def get_resource_path(*paths):
    """
    获取资源文件路径
    """
    log.info(f"获取资源文件路径: {paths}")
    resource = Path(__file__).parent.resolve() / "res" # 获取当前目录的资源文件夹路径
    return str(resource.joinpath(*paths))

should_check_update_res = should_check_update()
update_cache = load_update_cache()

if should_check_update_res:
    check_update_thread = ResultThread(target=check_update, args=("gitee", False), deamon=True)
    check_update_thread.start()
# 主窗口绘制和事件监听
class MainWindow(wx.Frame):
    def __init__(self, parent=None):
        # 初始化
        log.info("初始化主窗口")
        super().__init__(
            parent, 
            title="ClickMouse", 
            size=(400, 350),
            style = wx.DEFAULT_FRAME_STYLE & ~(wx.MAXIMIZE_BOX | wx.RESIZE_BORDER)# 去掉最大化和可调整的窗口大小
         )

        # 状态控制变量
        log.debug("初始化状态控制变量")
        self.running = False
        self.paused = False
        self.click_thread = None

        # 窗口初始化
        log.debug("加载图标和标题")
        self.Icon = wx.Icon(str(get_resource_path("icons", "icon.ico")), wx.BITMAP_TYPE_ICO)
        self.Title = "ClickMouse"

        # 创建面板
        log.debug("创建面板")
        panel = wx.Panel(self)
        panel.SetFocus()

        # 面板控件
        log.debug("创建控件")
        # 标题大字文本
        log.debug("创建标题大字")
        wx.StaticText(panel, -1, "鼠标连点器", wx.Point(115, 5), style=wx.ALIGN_CENTER).SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        # 定义按钮
        log.debug("创建按钮")
        self.button_left = wx.Button(panel, label="左键连点", pos=wx.Point(5, 60), size=wx.Size(100, 50))
        self.button_right = wx.Button(panel, label="右键连点", pos=wx.Point(280, 60), size=wx.Size(100, 50))
        self.pause_button = wx.Button(panel, label="暂停", pos=wx.Point(137, 60), size=wx.Size(100, 40))
        self.stop_button = wx.Button(panel, label="停止", size=wx.Size(100, 40))

        # 定义输入延迟的输入框
        log.debug("创建输入框")
        self.text_control_tip = wx.StaticText(panel, -1, "延迟(毫秒):", wx.Point(50, 250), style=wx.ALIGN_CENTER).SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        self.delay_input = wx.TextCtrl(panel, value="", pos=wx.Point(150, 245), size=wx.Size(200, 25))

        # 设置布局
        log.debug("设置布局")
        main_sizer = wx.BoxSizer(wx.VERTICAL) # 主布局
        main_sizer.AddSpacer(50)

        # 按钮的布局
        log.debug("创建按钮布局")
        # 第一行的布局
        log.debug("创建第一行布局")
        sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h1.Add(self.button_left, 1, wx.EXPAND | wx.ALL, 5)
        sizer_h1.AddSpacer(150)
        sizer_h1.Add(self.button_right, 1, wx.EXPAND | wx.ALL, 5)

        # 第二行的布局
        log.debug("创建第二行布局")
        sizer_h2 = wx.BoxSizer(wx.HORIZONTAL)

        self.create_contol_button(sizer_h2, self.pause_button)

        # 第三行的布局
        log.debug("创建第三行布局")
        sizer_h3 = wx.BoxSizer(wx.HORIZONTAL)
        self.create_contol_button(sizer_h3, self.stop_button)

        # 添加行布局到主布局
        log.debug("添加行布局到主布局")
        main_sizer.Add(sizer_h1, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sizer_h2, 0, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(sizer_h3, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(main_sizer) # 设置主布局

        # 创建菜单栏
        log.debug("创建菜单栏")
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_EXIT, "退出(&X)")
        file_menu.Append(ID_CLEAN_LOG, "清理日志(&C)")
        
        # 帮助菜单
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "关于(&A)")
        help_menu.Append(ID_UPDATE, "更新(&U)")
        help_menu.Append(ID_UPDATE_LOG, "更新日志(&L)")
        
        # 添加菜单到菜单栏
        log.debug("添加菜单到菜单栏")
        menubar.Append(file_menu, "文件(&F)")
        menubar.Append(help_menu, "帮助(&H)")
        
        # 设置菜单栏
        self.SetMenuBar(menubar)
        
        # 绑定事件
        log.debug("绑定事件")
        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.on_update, id=ID_UPDATE)
        self.Bind(wx.EVT_MENU, self.on_update_log, id=ID_UPDATE_LOG)
        self.Bind(wx.EVT_MENU, self.on_clean_log, id=ID_CLEAN_LOG)
        self.button_left.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_left)
        self.button_right.Bind(wx.EVT_LEFT_DOWN, self.on_mouse_right)
        # 判断更新结果
        self.Bind(wx.EVT_TIMER, self.on_check_update_result)
        self.check_update_timer = wx.Timer(self)
        self.check_update_timer.Start(100)  # 每100ms检查一次

        log.info("主窗口初始化完成")
        
    def on_check_update_result(self, event):
        """检查更新结果"""
        global result
        
        # 判断是否需要检查更新
        if should_check_update_res:
            if check_update_thread.is_alive():
                log.info("更新检查仍在进行中，忽略")
                return
        else:
            log.info("距离上次更新检查不到1天，使用缓存")

        # 判断是否需要缓存
        if should_check_update_res:
            result = check_update_thread.result()
        else:
            result = (update_cache["should_update"], update_cache["latest_version"]) # 使用缓存
        # 停止定时器
        self.check_update_timer.Stop()
        
        # 检查结果处理
        if result[1] != -1:  # -1表示函数出错
            if should_check_update_res:
                save_update_cache(should_update=result[0], latest_version=result[1]) # 缓存最新版本
            if result[0]:  # 检查到需要更新
                log.info("检查到更新")
                # 弹出更新窗口
                window = UpdateWindow(self)
                window.ShowModal()
                window.Destroy()
        else:
            # 元组类型是原函数设计的错误返回，这里可以处理错误
            log.error(f"检查更新错误: {result[0]}")
            wx.MessageBox(f"检查更新错误: {result[0]}", "错误", wx.ICON_ERROR)

    def on_exit(self, event):
        """退出程序"""
        log.info("退出程序")
        self.Close()

    def on_about(self, event):
        """显示关于窗口"""
        log.info("显示关于窗口")
        about_dialog = AboutWindow(self)
        about_dialog.ShowModal()
        about_dialog.Destroy()

    def on_update(self, event):
        """检查更新"""
        log.info("检查更新")
        if update_cache.get("should_update"):
            window = UpdateWindow(self)
            window.ShowModal()
            window.Destroy()
        else:
            wx.MessageBox("当前已是最新版本", "提示", wx.ICON_INFORMATION)
    
    def on_update_log(self, event):
        """显示更新日志"""
        log.info("显示更新日志")
        update_window = UpdateLogWindow(self)
        update_window.ShowModal()
        update_window.Destroy()
    
    def on_mouse_left(self, event):
        log.info("左键连点")
        # 停止当前运行的点击线程
        if self.click_thread and self.click_thread.is_alive():
            log.debug("停止当前运行的点击线程")
            self.running = False
            self.click_thread.join()  # 等待线程结束
        
        # 获取新参数并启动左键点击
        delay = self.delay_input.GetValue()
        self.mouse_click(button="left", delay=delay)

    def on_mouse_right(self, event):
        # 停止当前运行的点击线程
        log.info("右键连点")
        if self.click_thread and self.click_thread.is_alive():
            log.debug("停止当前运行的点击线程")
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
    
    def mouse_click(self, button: str, delay: int):
        """鼠标连点"""
        log.info("开始连点")
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
            log.error("用户输入错误：请输入有效的正整数延迟")
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
            log.info("连点器暂停或重启")
            self.paused = not self.paused
            if self.paused:
                self.pause_button.SetLabel("重启")
            else:
                self.pause_button.SetLabel("暂停")
            # 强制刷新按钮显示
            self.pause_button.Update()

        self.pause_button.Bind(wx.EVT_BUTTON, on_pause_click)

        # 启动线程
        log.info(f"启动连点线程")
        self.click_thread = threading.Thread(target=click_loop)
        self.click_thread.daemon = True
        self.click_thread.start()

        # 绑定控制按钮
        self.stop_button.Bind(wx.EVT_BUTTON, lambda e: setattr(self, 'running', False))
        self.stop_button.Bind(wx.EVT_BUTTON, lambda e: (
        setattr(self, 'running', False),
        self.pause_button.SetLabel("暂停")
    ))
        
    def on_clean_log(self, event):
        """清理日志"""
        log.info("清理日志")
        directory = "logs/"
        path = Path(directory)
        if path.exists() and path.is_dir():
            for child in path.iterdir():
                if child.is_file():
                    try:
                        child.unlink() # 删除文件
                        log.info(f"删除文件: {child}") # 记录日志
                    except PermissionError as e:
                        log.error(f"无法删除文件: {child},PermissionError: {e}") # 记录日志
                else:
                    log.warning(f"无法删除文件夹: {child}") # 记录日志

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
        open_url("https://github.com/xystudio889/pyClickMouse")

class UpdateLogWindow(wx.Dialog):
    def __init__(self, parent=MainWindow):
        super().__init__(parent, title="更新日志", size=(300, 750))# 初始化

        point_y = 5 # 初始y坐标
        update_logs: dict[str, list[str, wx.Size]] = {
            "2025/08/04    v1.1.0.0" : ["对'关于'界面更新：\n\t添加了\"支持作者\"按钮\n\t移动'更新按钮'到主窗口的'帮助'菜单\n添加了找不到焦点提示", self.size(70)],
            "2025/08/08    v1.1.2.0" : ["添加了“更新日志”界面", self.size()],
            "2025/08/12    v1.1.2.3" : ["修改了部分显示字符\n修复了当关闭\"更新日志\"时，主窗口一并关闭的问题", self.size(60)],
            "2025/08/21    v2.0.0.4" : ["使用python重构代码", self.size()],
            "2025/08/24    v2.1.0.5" : ["添加了日志和自动更新系统", self.size()],
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
        open_url("https://github.com/xystudio889/pyClickMouse/releases")

    def size(self, height: int = 20) -> wx.Size:
        return wx.Size(270, height)

class UpdateWindow(wx.Dialog):
    def __init__(self, parent=MainWindow):
        super().__init__(parent, title="发现更新", size=(200, 180)) # 初始化
        # 创建面板
        panel = wx.Panel(self)
        # 面板控件
        wx.StaticText(panel, -1, f"发现新版本", wx.Point(5, 5)).SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        wx.StaticText(panel, -1, f"当前版本：{__version__}\n最新版本：{result[1]}\n暂时不显示更新日志，请手动到github releases查看。", wx.Point(5, 30), wx.Size(180, 70))
        # 按钮
        wx.Button(panel, ID_UPDATE, "更新", wx.Point(5, 110))
        wx.Button(panel, wx.ID_CANCEL, "取消", wx.Point(100, 110))
        # 绑定事件
        self.Bind(wx.EVT_BUTTON, self.on_update, id=ID_UPDATE)

    def on_update(self, event):
        """更新"""
        open_url("https://github.com/xystudio889/pyClickMouse/releases")

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
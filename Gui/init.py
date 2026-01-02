from PySide6.QtCore import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys
app = QApplication(sys.argv)

import os
from pathlib import Path
import winreg # 注册表编辑
import ctypes # 管理员运行
import pyperclip # 复制错误信息
import win32com.client # 创建快捷方式
import zipfile # 解压文件
import json # 读写json文件
from sharelibs import (get_resource_path, settings, run_software) # 共享库
from uiStyles import PagesUI
from uiStyles.WidgetStyles import (styles)
from datetime import datetime

with open(get_resource_path('langs', 'init.json'), 'r', encoding='utf-8') as f:
    langs = json.load(f)
    
with open(get_resource_path('package_info.json'), 'r', encoding='utf-8') as f:
    packages_info = json.load(f)
    
software_reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'

def get_lang(lang_package_id, lang_id = None):
    lang_id = settings.get('select_lang', 0) if lang_id is None else lang_id
    for i in langs:
        if i['lang_id'] == 0: # 设置默认语言包
            lang_text = i['lang_package']
        if i['lang_id'] == lang_id: # 设置目前语言包
            lang_text = i['lang_package']
    try:
        return lang_text[lang_package_id]
    except KeyError:
        return 'Language not found'

def save_settings(settings):
    '''
    保存设置
    '''
    with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)

data_path = Path('data')

def create_shortcut(path, target, description, work_dir = None, icon_path = None):
    # 创建快捷方式
    icon_path = target if icon_path is None else icon_path
    work_dir = os.path.dirname(target) if work_dir is None else work_dir
    
    shell = win32com.client.Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.TargetPath = target # 目标程序
    shortcut.WorkingDirectory = work_dir # 工作目录
    shortcut.IconLocation = icon_path # 图标（路径,图标索引）
    shortcut.Description = description # 备注描述
    shortcut.Save()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def get_install_size():
    pass
        
def extract_zip(file_path, extract_path):
    '''
    解压zip文件
    '''
    with zipfile.ZipFile(file_path, 'r') as f:
        f.extractall(extract_path)
    
def check_reg_key(subkey):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_READ):
            return True
    except:
        return False

def read_reg_key(key, value):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_READ) as k:
            return winreg.QueryValueEx(k, value)[0]
    except:
        return None

def get_system_language():
    '''通过Windows注册表获取系统语言'''
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Control Panel\International')
        lang, _ = winreg.QueryValueEx(key, 'LocaleName')
        return lang
    except Exception:
        return 'en-US'
    
def parse_system_language_to_lang_id():
    '''将系统语言转换为语言ID'''
    system_lang = get_system_language()
    for i in langs:
        if i['is_official']:
            if i['lang_info'].get('lang_system_name', 'en-US') == system_lang:
                return i['lang_id']
    return 0
    
def get_dir_size_for_reg(dir):
    size = 0
    
    for root, dirs, files in os.walk(dir):
        for file in files:
            try:
                size += os.path.getsize(os.path.join(root, file))
            except:
                print(f'Error: {file} does not exist')
    return size // 1024

def import_package(package_id, **config):
    for i in packages_info:
        if i['package_id'] == package_id:
            package = i
    package.update(config)
    return package

class ColorGetter(QObject):
    style_changed = Signal(str)
    
    def __init__(self):
        super().__init__()

        self.current_theme = self.load_theme()
    
        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(100)
    
    def load_theme(self):
        theme = None

        theme = QApplication.styleHints().colorScheme()
        if theme == Qt.ColorScheme.Dark:
            theme = 'dark'
        elif theme == Qt.ColorScheme.Light:
            theme = 'light'
    
        return theme

    def check_and_apply_theme(self):
        '''检查主题是否变化，变化则重新应用'''
        new_theme = self.load_theme()
        
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_global_theme()

    def apply_global_theme(self):
        '''根据当前主题，为整个应用设置全局样式表'''
        global select_styles, selected_style, main_style, default_style, big_title
        
        self.style_changed.emit(self.current_theme)
        
        select_styles = styles[self.current_theme]
        selected_style = select_styles['selected_button']
        main_style = select_styles['main']
        default_style = main_style + (selected_style.replace('QPushButton', 'QPushButton:pressed'))
        big_title = select_styles['big_text']

        app.setStyleSheet(default_style)  # 全局应用

icon = QIcon(str(get_resource_path('icons', 'clickmouse', 'icon.ico')))

getter = ColorGetter()

class InstallWindow(PagesUI):
    def __init__(self):
        super().__init__(['hello', 'read_license', 'set_path', 'set_link', 'set_components', 'install', 'finish', 'cancel', 'error'])
        
        self.setWindowTitle('ClickMouse')
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 500, 375)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小
        
        # colorGetter属性
        getter.style_changed.connect(self.on_style_changed)
        self.on_style_changed(getter.current_theme)
        
    def init_ui(self):
        '''初始化UI'''
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 移除边距
        main_layout.setSpacing(0)  # 移除间距
        
        # 创建顶部白色区域
        self.top_widget = QWidget()
        self.top_widget.setFixedHeight(50)  # 设置顶部高度
        
        # 创建顶部区域的内容布局
        self.top_layout = QHBoxLayout(self.top_widget)
        
        image_label = QLabel()

        # 加载图片
        image_label.setPixmap(self.loadImage(get_resource_path('icons', 'clickmouse', 'icon.png'), 32, 32))
        
        # 加载文字
        title_label = QLabel('ClickMouse 安装向导')
        title_label.setStyleSheet(big_title)
        
        # 布局
        self.top_layout.addWidget(image_label)
        self.top_layout.addWidget(title_label)
        self.top_layout.addStretch(1) # 居左显示

        # 将顶部和内容区域添加到主布局
        main_layout.addWidget(self.top_widget)
        
        # 页面堆叠控件
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # 按钮布局
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(0)
        
        # 上一步按钮
        self.prev_btn = QPushButton('上一步')
        self.prev_btn.clicked.connect(self.on_prev)
        self.button_layout.addWidget(self.prev_btn)
        
        # 下一步/错误重叠容器
        self.next_error_container = QWidget()
        self.next_error_layout = QHBoxLayout(self.next_error_container)
        
        # 下一步按钮
        self.next_btn = QPushButton('下一步')
        self.next_btn.clicked.connect(self.on_next)
        self.next_error_layout.addWidget(self.next_btn)
        
        # 错误重叠容器
        self.copy_error_btn = QPushButton('复制错误信息')
        self.copy_error_btn.clicked.connect(self.copy_error)
        self.next_error_layout.addWidget(self.copy_error_btn)
        
        # 取消/完成按钮容器（重叠放置）
        self.action_button_container = QWidget()
        self.action_button_layout = QHBoxLayout(self.action_button_container)
        
        # 取消按钮
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.cancel)
        self.action_button_layout.addWidget(self.cancel_btn)
        
        # 完成按钮
        self.finish_btn = QPushButton('完成')
        self.finish_btn.clicked.connect(self.close)
        self.action_button_layout.addWidget(self.finish_btn)
        
        self.button_layout.addWidget(self.next_error_container)
        self.button_layout.addWidget(self.action_button_container)
        
        main_layout.addLayout(self.button_layout)
        
    def on_style_changed(self, current_theme):
        if current_theme == 'dark':
            self.top_widget.setStyleSheet('background-color: black;')
        else:
            self.top_widget.setStyleSheet('background-color: white;')
        
    def show_page(self, page_index):
        '''显示指定页面'''
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        
        match page_index:
            case self.PAGE_hello:
                # 第一页：欢迎
                page_layout.addWidget(QLabel('欢迎使用 clickMouse 安装向导!\n\n这个程序将简单的使用几分钟时间，帮助你完成安装。\n点击下一步开启安装助手。'))
            case self.PAGE_read_license:
                # 第二页：阅读许可协议
                with open(get_resource_path('license.txt'), 'r', encoding='utf-8') as f:
                    license_text = f.read()

                edit = QTextEdit()
                edit.setReadOnly(True)
                edit.setText(license_text)
                
                self.emua_checkbox = QCheckBox('我已阅读并同意许可协议')

                # 页面布局
                page_layout.addWidget(QLabel('请先阅读下方的许可协议，同意后，点击下一步。'))
                page_layout.addWidget(edit)
                page_layout.addWidget(self.emua_checkbox)
                
                # 信号连接
                self.emua_checkbox.stateChanged.connect(self.set_emua_checkbox)
            case self.PAGE_set_path:
                # 第三页：设置安装路径
                path_edit = QLineEdit(str(Path.cwd()))
                path_edit.setReadOnly(True)

                page_layout.addWidget(QLabel('这是软件安装路径：'))
                page_layout.addWidget(path_edit)
            case self.PAGE_set_link:
                self.create_desktop_shortcut = True
                self.create_start_menu_shortcut = True

                # 第四页：设置快捷方式
                desktop_checkbox = QCheckBox('创建桌面快捷方式')
                desktop_checkbox.setChecked(self.create_desktop_shortcut)
                
                start_menu_checkbox = QCheckBox('创建开始菜单快捷方式')
                start_menu_checkbox.setChecked(self.create_start_menu_shortcut)
                
                page_layout.addWidget(QLabel('请选择你要创建的快捷方式：'))
                page_layout.addWidget(desktop_checkbox)
                page_layout.addWidget(start_menu_checkbox)
                
                # 信号连接
                desktop_checkbox.stateChanged.connect(self.set_desktop_checkbox)
                start_menu_checkbox.stateChanged.connect(self.set_start_menu_checkbox)
            case self.PAGE_set_components:
                # 第四页：设置组件
                # 初始化数据
                self.all_components = ['clickMouse 主程序']
                self.selected_components = ['clickMouse 主程序']
                self.protected_components = ['clickMouse 主程序']
                self.templates = {
                    '默认': ['clickMouse 主程序'],
                    '精简': self.protected_components,
                    '全选': self.all_components,
                }

                # 创建主水平布局
                main_layout = QHBoxLayout()
                
                self.unselected_list = QListView()
                self.unselected_model = QStandardItemModel()
                self.unselected_list.setModel(self.unselected_model)

                # 中间：控制按钮
                control_layout = QVBoxLayout()
                control_layout.addStretch()
                
                # 模板选择区域
                template_layout = QHBoxLayout()
                
                self.template_combo = QComboBox()
                self.template_combo.addItems(list(self.templates.keys()) + ['自定义'])
                
                # 布局
                template_layout.addWidget(QLabel('模板:'))
                template_layout.addWidget(self.template_combo)
                template_layout.addStretch()
                
                self.add_btn = QPushButton('>> 添加')
                self.remove_btn = QPushButton('<< 移除')
                
                control_layout.addLayout(template_layout)
                control_layout.addStretch(1)
                control_layout.addWidget(self.add_btn)
                control_layout.addWidget(self.remove_btn)
                control_layout.addStretch(1)

                # 已选择组件列表
                right_layout = QVBoxLayout()
                right_layout.addWidget(QLabel('已选择组件:'))
                
                self.selected_list = QListView()
                self.selected_model = QStandardItemModel()
                self.selected_list.setModel(self.selected_model)

                # 添加到主布局
                main_layout.addWidget(self.unselected_list, 5)
                main_layout.addLayout(control_layout, 1)
                main_layout.addWidget(self.selected_list, 5)
                
                page_layout.addWidget(QLabel('请选择你要安装的组件：'))
                page_layout.addLayout(main_layout)

                # 初始化列表
                self.update_components_lists()
            case self.PAGE_install:
                self.install_status = ''
                # 第五页：安装
                page_layout.addWidget(QLabel('正在安装 ClickMouse...'))
            case self.PAGE_finish:
                # 第六页：完成        
                self.run_clickmouse = QCheckBox('运行 ClickMouse 主程序')
                self.run_clickmouse.setChecked(True)
                
                page_layout.addWidget(QLabel('安装完成！'))
                page_layout.addWidget(self.run_clickmouse)
            case self.PAGE_cancel:
                # 第七页：取消
                page_layout.addWidget(QLabel('安装已取消！'))
            case self.PAGE_error:
                # 第八页：错误
                self.error_label = QLabel('发生错误：\n在 发生安装错误：\n请重新安装，若错误持续，请联系作者。')
                page_layout.addWidget(self.error_label)
        
        page_layout.addStretch(1) # 居上显示
        return page_widget
    
    def copy_error(self):
        '''复制错误信息到剪贴板'''
        pyperclip.copy(self.error_label.text())
        QMessageBox.information(self, '提示', '错误信息已复制到剪贴板')
    
    def setup_connections(self):
        '''设置信号与槽的连接'''
        self.add_btn.clicked.connect(self.add_selected)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.template_combo.currentTextChanged.connect(self.apply_template)
        
    def set_desktop_checkbox(self, checked):
        '''设置桌面快捷方式'''
        self.create_desktop_shortcut = checked
    
    def set_start_menu_checkbox(self, checked):
        '''设置开始菜单快捷方式'''
        self.create_start_menu_shortcut = checked

    def update_components_lists(self):
        '''更新左右两个列表的显示'''
        # 更新未选择列表
        self.unselected_model.clear()
        unselected = [comp for comp in self.all_components 
                     if comp not in self.selected_components]
        
        for component in unselected:
            item = QStandardItem(component)
            if component in self.protected_components:
                item.setForeground(Qt.gray)
            self.unselected_model.appendRow(item)

        # 更新已选择列表
        self.selected_model.clear()
        for component in self.selected_components:
            item = QStandardItem(component)
            if component in self.protected_components:
                item.setForeground(Qt.gray)
                item.setEditable(False)  # 保护项不可编辑
            self.selected_model.appendRow(item)

    @Slot()
    def add_selected(self):
        '''添加选中的组件'''
        indexes = self.unselected_list.selectedIndexes()
        for index in indexes:
            component = self.unselected_model.itemFromIndex(index).text()
            if component not in self.selected_components:
                self.selected_components.append(component)
        
        self.update_components_lists()
        self.template_combo.setCurrentText('自定义')

    @Slot()
    def remove_selected(self):
        '''移除选中的组件（排除保护组件）'''
        indexes = self.selected_list.selectedIndexes()
        components_to_remove = []
        
        for index in indexes:
            component = self.selected_model.itemFromIndex(index).text()
            # 检查是否是保护组件
            if component not in self.protected_components:
                components_to_remove.append(component)
        
        for component in components_to_remove:
            self.selected_components.remove(component)
        
        self.update_components_lists()
        self.template_combo.setCurrentText('自定义')

    @Slot(str)
    def apply_template(self, template_name):
        '''应用选择的模板'''
        if template_name == '自定义':
            return
        
        if template_name in self.templates:
            # 应用模板，但要保留保护组件
            template_components = self.templates[template_name]
            # 确保保护组件被包含
            for protected_comp in self.protected_components:
                if protected_comp not in template_components:
                    template_components.append(protected_comp)
            
            self.selected_components = template_components.copy()
            self.update_components_lists()
    
    def loadImage(self, image_path, width, height):
        '''加载并显示图片'''
        # 创建QPixmap对象
        pixmap = QPixmap(image_path)
        
        # 按比例缩放图片以适应标签大小
        scaled_pixmap = pixmap.scaled(
            width, 
            height,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        return scaled_pixmap
    
    def set_emua_checkbox(self, checked):
        self.next_btn.setEnabled(checked)
    
    def update_buttons(self):
        if (self.current_page >= self.PAGE_finish):
            # 完成页：只显示完成按钮
            self.prev_btn.setVisible(False)
            self.next_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            self.finish_btn.setVisible(True)
        else:
            # 正常页面：显示上一步、下一步、取消
            self.prev_btn.setVisible(self.current_page != 0)
            self.next_btn.setVisible(True)
            self.cancel_btn.setVisible(True)
            self.finish_btn.setVisible(False)

        # 禁用状态
        if self.current_page == self.PAGE_read_license:
            self.next_btn.setEnabled(self.emua_checkbox.isChecked())
        else: 
            self.next_btn.setEnabled(True)
            
        # 复制错误
        if self.current_page == self.PAGE_error:
            self.copy_error_btn.setVisible(True)
        else:
            self.copy_error_btn.setVisible(False)
            
        if self.current_page == self.PAGE_install:
            self.next_btn.setVisible(False)
            self.prev_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            
            self.install()
            
        if self.current_page == self.PAGE_set_components and not(has_package):
            self.set_page(self.PAGE_install)
            
    def set_status(self, status):
        '''设置状态栏'''
        self.install_status = status
        
    def install(self):
        '''安装'''
        try:
            self.set_status('初始化...')
            install_path = Path.cwd()
            self.set_status('正在创建包管理器文件...')
            package = []
            package.append(import_package('xystudio.clickmouse', install_location=str(install_path), create_in_start_menu=self.create_start_menu_shortcut, create_desktop_shortcut=self.create_desktop_shortcut))
            
            self.set_status('解压安装包...')
            self.set_status('正在写入包管理器文件...')
            with open(fr'{install_path}\packages.json', 'w', encoding='utf-8') as f:
                json.dump(package, f)
                
            # 卸载功能

            self.set_status('正在创建安装信息...')
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\clickmouse'
            )
            winreg.SetValue(key, '', winreg.REG_SZ, fr'{install_path}\main.exe')
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_SZ, f'{install_path}')
            winreg.CloseKey(key)

            self.set_status('正在创建卸载信息...')
            uninstall_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse')
            winreg.SetValueEx(uninstall_key, 'DisplayName', 0, winreg.REG_SZ, 'clickmouse')
            winreg.SetValueEx(uninstall_key, 'Publisher', 0, winreg.REG_SZ, f'xystudio')
            winreg.SetValueEx(uninstall_key, 'InstallLocation', 0, winreg.REG_SZ, f'{install_path}')
            winreg.SetValueEx(uninstall_key, 'UninstallString', 0, winreg.REG_SZ, f'{install_path}/uninstall.exe')
            winreg.SetValueEx(uninstall_key, 'ModifyString', 0, winreg.REG_SZ, f'{install_path}/install_pks.exe')
            winreg.SetValueEx(uninstall_key, 'RepairString', 0, winreg.REG_SZ, f'{install_path}/repair.exe')
            with open(get_resource_path('versions.json'), 'r', encoding='utf-8') as f:
                version = json.load(f)['clickmouse']
            winreg.SetValueEx(uninstall_key, 'DisplayVersion', 0, winreg.REG_SZ, version)

            winreg.SetValueEx(uninstall_key, 'EstimatedSize', 0, winreg.REG_DWORD, int(get_dir_size_for_reg(install_path)))
            winreg.SetValueEx(uninstall_key, 'URLInfoAbout', 0, winreg.REG_SZ, 'https://www.github.com/xystudio/pyclickmouse')
            winreg.SetValueEx(uninstall_key, 'DisplayIcon', 0, winreg.REG_SZ, fr'{install_path}\res\icons\clickmouse\icon.ico')

            winreg.CloseKey(uninstall_key)

            self.set_status('正在创建快捷方式...')
            if self.create_start_menu_shortcut:
                create_shortcut(fr'C:\ProgramData\Microsoft\Windows\Start Menu\Programs\clickmouse.lnk', fr'{install_path}\main.exe', '鼠标连点器')
            if self.create_desktop_shortcut:
                create_shortcut(fr'{os.path.expanduser('~')}\Desktop\clickmouse.lnk', fr'{install_path}\main.exe', '鼠标连点器')
            self.set_page(self.PAGE_finish)
        except Exception as e:
            self.error_label.setText(f'发生错误：\n在 {self.install_status} 发生安装错误：{e}\n请重新安装，若错误持续，请联系作者。')
            self.set_page(self.PAGE_error)
            
    def cancel(self):
        '''取消安装'''
        self.set_page(self.PAGE_cancel)
        
    def on_next(self):
        if self.current_page == self.PAGE_set_components:
            # 第四页：提示
            message =QMessageBox.question(
                self,
                '提示',
                f'''即将安装以下组件:
{'\n'.join(self.selected_components)}
并创建以下快捷方式：
{'桌面快捷方式' if self.create_desktop_shortcut else ''}
{'开始菜单快捷方式' if self.create_start_menu_shortcut else ''},
是否继续？''',
            QMessageBox.Yes | QMessageBox.No,
            )
            if message == QMessageBox.No:
                self.cancel()
                return
        super().on_next()
        
    def closeEvent(self, event):
        if self.current_page < self.PAGE_finish:
            event.ignore()
            self.cancel()
        elif self.current_page == self.PAGE_finish:
            if self.run_clickmouse.isChecked():
                run_software('main.py', 'main.exe')
                with open(data_path / 'first_run', 'w'):pass # 标记为第一次运行
                event.accept()
        else:
            event.accept()

if __name__ == '__main__':
    has_package = True
    if not get_resource_path('packages'):
        QMessageBox.warning(None, '错误', '再编译版安装包不会添加，请自行打包（格式必须为zip）并放入res/packages文件夹下。')
        has_package = False

    if check_reg_key(r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'):
        QMessageBox.critical(None, '错误', '检测到已安装 ClickMouse。')
        with open(get_resource_path('first_run'), 'w'):pass
        sys.exit(1)

    if is_admin():  # 管理员权限
        window = InstallWindow()
        window.show()
    else:
        QMessageBox.critical(None, '错误', '请以管理员身份运行本程序。')
    sys.exit(app.exec())
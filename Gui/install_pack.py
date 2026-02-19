# 加载框架
from PySide6.QtWidgets import QApplication
import sys
app = QApplication(sys.argv)
from uiStyles.QUI import *
from uiStyles import PagesUI, UMessageBox, MessageButtonTemplate
    
def import_package(package_id: str):
    for i in packages_info:
        if i['package_name'] == package_id:
            return i
    raise ValueError(f'Package {package_id} not found.')

def save_settings(settings):
    '''
    保存设置
    '''
    with open(data_path / 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f)

def extract_zip(file_path, extract_path):
    '''
    解压zip文件
    '''
    try:
        with zipfile.ZipFile(file_path, 'r') as f:
            f.extractall(extract_path)
    except:
        pass
        
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
    
def get_dir_size_for_reg(dir):
    size = 0
    for root, dirs, files in os.walk(dir):
        for file in files:
            try:
                size += os.path.getsize(os.path.join(root, file))
            except:
                pass
    return size // 1024

def get_packages():
    package_index = [] # 包索引
    
    # 加载包信息
    for package in packages_source:
        package_index.append(get_lang(package.get('package_name_index', None)))
    return (package_index)

def get_list_diff(list1: list, list2: list) -> list:
    '''
    获取两个列表的差集

    :param list1: 列表1
    :param list2: 列表2
    :return: 他们的差集，如果是list2中增加了元素，则返回'+多的元素'，如果在list2中删除了元素，则返回'-少的元素'
    '''
    set1 = set(list1)
    set2 = set(list2)
   
    diff_list = []

    for i in set1 - set2:# 被删除元素集合
        diff_list.append(f"-{i}")

    for i in set2 - set1:# 被添加元素集合
        diff_list.append(f"+{i}")
    
    return diff_list
        
def new_color_bar(obj):
    '''
    给创建添加样式标题栏
    '''
    getter.style_changed.connect(lambda: QTimer.singleShot(settings.get('soft_delay', 1), lambda: getter.apply_titleBar(obj)))
    getter.style_changed.emit(getter.current_theme)

class Refresh:
    def __init__(self):
        self.steps = [
            self.refresh_title,
        ]
    
    def run(self):
        self.do_step(self.steps)
                
    def do_step(self, codes):
        # 尝试执行代码
        for code in codes:
            try:
                code()
            except Exception:
                pass
        
    def refresh_title(self):
        QTimer.singleShot(settings.get('soft_delay', 1), lambda: getter.style_changed.emit(getter.current_theme))
        
class MessageBox(UMessageBox):
    @staticmethod
    def new_msg(parent, 
                title: str, 
                text: str, 
                icon: QMessageBox.Icon, 
                buttons: MessageButtonTemplate = MessageButtonTemplate.OK,
                defaultButton: MessageButtonTemplate = MessageButtonTemplate.OK):
        
        msg_box = UMessageBox.new_msg(parent, title, text, icon, buttons, defaultButton)
        new_color_bar(msg_box)

        return msg_box

class ColorGetter(QObject):
    style_changed = Signal(str)
    
    def __init__(self):
        global refresh

        super().__init__()
        
        # 加载刷新服务
        refresh = Refresh()
        
        # 记录当前主题
        self.style = settings.get('select_style', 0)

        self.current_theme, self.windows_theme = self.load_theme()
        self.current_theme = self.current_theme.replace('auto-', '')

        # 初始化时应用一次主题
        self.apply_global_theme()

        # 使用定时器定期检测主题变化
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_and_apply_theme)
        self.timer.start(settings.get('style_delay', 1000))
    
    def load_theme(self):
        theme = None
        
        if self.style == 0:
            theme = QApplication.styleHints().colorScheme()
            if theme == Qt.ColorScheme.Dark:
                theme = 'auto-dark'
            elif theme == Qt.ColorScheme.Light:
                theme = 'auto-light'

        windows_theme = QApplication.styleHints().colorScheme()   
        if theme == Qt.ColorScheme.Dark:
            windows_theme = 'dark'
        elif theme == Qt.ColorScheme.Light:
            windows_theme = 'light'
        
        for k, v in maps.items():
            if v == settings.get('select_style', 0):
                theme = k
    
        return theme, windows_theme

    def check_and_apply_theme(self):
        '''检查主题是否变化，变化则重新应用'''
        self.style = settings.get('select_style', 0)
        
        new_theme, new_windows_theme = self.load_theme()
        
        if new_theme != self.current_theme:
            self.current_theme = new_theme
            self.apply_global_theme()
            
        if new_windows_theme != self.windows_theme:
            self.windows_theme = new_windows_theme
            refresh.run()  # 运行刷新服务
            
    def apply_titleBar(self, window: QMainWindow | QDialog):
        '''应用标题栏样式'''
        hwnd = window.winId().__int__()
        
        if select_styles.css_data['.meta']['mode'] == 'dark':
            is_dark_mode = 1
        else:
            is_dark_mode = 0

        # 设置深色模式
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            wintypes.HWND(hwnd),
            DWMWA_USE_IMMERSIVE,
            ctypes.byref(wintypes.INT(is_dark_mode)),
            ctypes.sizeof(wintypes.INT)
        )

    def apply_global_theme(self):
        '''根据当前主题，为整个应用设置全局样式表'''
        global select_styles

        self.style_changed.emit(self.current_theme)

        current_theme = self.current_theme.replace('auto-', '')
        
        select_styles = styles[current_theme]
            
        app.setStyleSheet(select_styles.css_text)  # 全局应用
        refresh.run()  # 运行刷新服务

class InstallWindow(PagesUI):
    def __init__(self):
        self.all_packages_name = [get_lang(i['package_name_index'], source=package_langs) for i in packages_source]
        super().__init__(['hello', 'read_license', 'set_path', 'set_link', 'set_components', 'install', 'finish', 'cancel', 'error', 'finish_nochanges'])
        
        self.setWindowTitle(get_ipk_lang('01'))
        self.setWindowIcon(icon)
        self.setGeometry(100, 100, 500, 375)
        self.setWindowFlags(
            Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
        ) # 设置窗口属性
        
        self.setFixedSize(self.width(), self.height()) # 固定窗口大小
        
        new_color_bar(self)
        self.install_status = ''
        
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
        self.top_widget.setProperty('class', 'top_widget')  # 设置样式类名
        
        # 创建顶部区域的内容布局
        self.top_layout = QHBoxLayout(self.top_widget)
        
        image_label = QLabel()

        # 加载图片
        clickmouse_icon = get_icon('icon')
        image_label.setPixmap(clickmouse_icon.pixmap(32, 32))
        
        # 加载文字
        title_label = QLabel(get_ipk_lang('01'))
        title_label.setProperty('class', 'big_text_16')
        
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
        self.prev_btn = QPushButton(get_ipk_lang('02'))
        self.prev_btn.clicked.connect(self.on_prev)
        self.button_layout.addWidget(self.prev_btn)
        
        # 下一步/错误重叠容器
        self.next_error_container = QWidget()
        self.next_error_layout = QHBoxLayout(self.next_error_container)
        
        # 下一步按钮
        self.next_btn = QPushButton(get_ipk_lang('03'))
        self.next_btn.clicked.connect(self.on_next)
        self.next_error_layout.addWidget(self.next_btn)
        
        # 错误重叠容器
        self.copy_error_btn = QPushButton(get_ipk_lang('04'))
        self.copy_error_btn.clicked.connect(self.copy_error)
        self.next_error_layout.addWidget(self.copy_error_btn)
        
        # 取消/完成按钮容器（重叠放置）
        self.action_button_container = QWidget()
        self.action_button_layout = QHBoxLayout(self.action_button_container)
        
        # 取消按钮
        self.cancel_btn = QPushButton(get_ipk_lang('05'))
        self.cancel_btn.clicked.connect(self.cancel)
        self.action_button_layout.addWidget(self.cancel_btn)
        
        # 完成按钮
        self.finish_btn = QPushButton(get_ipk_lang('06'))
        self.finish_btn.clicked.connect(self.close)
        self.action_button_layout.addWidget(self.finish_btn)
        
        self.button_layout.addWidget(self.next_error_container)
        self.button_layout.addWidget(self.action_button_container)
        
        main_layout.addLayout(self.button_layout)
        
    def show_page(self, page_index):
        '''显示指定页面'''
        page_widget = QWidget()
        page_layout = QVBoxLayout(page_widget)
        
        match page_index:
            case self.PAGE_hello:
                # 第一页：欢迎
                page_layout.addWidget(QLabel(get_ipk_lang('07')))
            case self.PAGE_read_license:
                # 第二页：阅读许可协议
                with open(get_resource_path('license.txt'), 'r', encoding='utf-8') as f:
                    license_text = f.read()

                edit = QTextEdit()
                edit.setReadOnly(True)
                edit.setText(license_text)
                
                self.emua_checkbox = UCheckBox(get_ipk_lang('08'))

                # 页面布局
                page_layout.addWidget(QLabel(get_ipk_lang('09')))
                page_layout.addWidget(edit)
                page_layout.addWidget(self.emua_checkbox)
                
                # 信号连接
                self.emua_checkbox.checkStateChanged.connect(self.set_emua_checkbox)
            case self.PAGE_set_path:
                # 第三页：设置安装路径
                path_edit = QLineEdit(str(Path.cwd()))
                path_edit.setReadOnly(True)

                page_layout.addWidget(QLabel(get_ipk_lang('0a')))
                page_layout.addWidget(path_edit)
            case self.PAGE_set_link:
                self.create_desktop_shortcut = True
                self.create_start_menu_shortcut = True

                # 第四页：设置快捷方式
                desktop_checkbox = UCheckBox(get_ipk_lang('0b'))
                desktop_checkbox.setChecked(self.create_desktop_shortcut)
                
                start_menu_checkbox = UCheckBox(get_ipk_lang('0c'))
                start_menu_checkbox.setChecked(self.create_start_menu_shortcut)
                
                page_layout.addWidget(QLabel(get_ipk_lang('0d')))
                page_layout.addWidget(desktop_checkbox)
                page_layout.addWidget(start_menu_checkbox)
                
                # 信号连接
                desktop_checkbox.checkStateChanged.connect(self.set_desktop_checkbox)
                start_menu_checkbox.checkStateChanged.connect(self.set_start_menu_checkbox)
            case self.PAGE_set_components:
                # 第四页：设置组件
                # 初始化数据
                with open(get_resource_path('vars', 'init_packages.json'), 'r', encoding='utf-8') as f:
                    init_packages = json.load(f)
                    
                if is_ipk:
                    self.all_components = [get_lang(i['package_name_index'], source=package_langs) for i in packages_info]
                    self.selected_components = self.all_packages_name.copy()
                    self.protected_components = [get_lang(i, source=package_langs) for i in init_packages['protected_components']]
                    self.templates = {
                        get_ipk_lang('21'): self.selected_components,
                        get_ipk_lang('0e'): [get_lang(i, source=package_langs) for i in init_packages['selected_components']],
                        get_ipk_lang('0f'): self.protected_components,
                        get_ipk_lang('10'): self.all_components,
                    }
                else:
                    self.all_components = [get_lang(i['package_name_index'], source=package_langs, lang_id=system_lang) for i in packages_info]
                    self.selected_components = [get_lang(i, source=package_langs, lang_id=system_lang) for i in init_packages['selected_components']]
                    self.protected_components = [get_lang(i, source=package_langs, lang_id=system_lang) for i in init_packages['protected_components']]
                    self.templates = {
                        get_ipk_lang('0e'): self.selected_components,
                        get_ipk_lang('0f'): self.protected_components,
                        get_ipk_lang('10'): self.all_components,
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
                self.template_combo.addItems(list(self.templates.keys()) + [get_ipk_lang('11')])
                
                # 布局
                template_layout.addWidget(QLabel(get_ipk_lang('12')))
                template_layout.addWidget(self.template_combo)
                template_layout.addStretch()
                
                self.add_btn = QPushButton(get_ipk_lang('13'))
                self.remove_btn = QPushButton(get_ipk_lang('14'))
                
                control_layout.addLayout(template_layout)
                control_layout.addStretch(1)
                control_layout.addWidget(self.add_btn)
                control_layout.addWidget(self.remove_btn)
                control_layout.addStretch(1)

                # 已选择组件列表
                right_layout = QVBoxLayout()
                right_layout.addWidget(QLabel(get_ipk_lang('22')))
                
                self.selected_list = QListView()
                self.selected_model = QStandardItemModel()
                self.selected_list.setModel(self.selected_model)

                # 添加到主布局
                main_layout.addWidget(self.unselected_list, 5)
                main_layout.addLayout(control_layout, 1)
                main_layout.addWidget(self.selected_list, 5)
                
                page_layout.addWidget(QLabel(get_ipk_lang('15')))
                page_layout.addLayout(main_layout)

                # 初始化列表
                self.update_components_lists()
                
                # 信号连接
                self.add_btn.clicked.connect(self.add_selected)
                self.remove_btn.clicked.connect(self.remove_selected)
                self.template_combo.currentTextChanged.connect(self.apply_template)
            case self.PAGE_install:
                # 第五页：安装
                pass
            case self.PAGE_finish:
                # 第六页：完成
                if is_ipk:
                    page_layout.addWidget(QLabel(get_ipk_lang('23')))
                else:
                    self.run_clickmouse = UCheckBox(get_ipk_lang('16'))
                    self.run_clickmouse.setChecked(True)
                    page_layout.addWidget(QLabel(get_ipk_lang('17')))
                    page_layout.addWidget(self.run_clickmouse)
            case self.PAGE_cancel:
                # 第七页：取消
                page_layout.addWidget(QLabel(get_ipk_lang('18')))
            case self.PAGE_error:
                # 第八页：错误
                self.error_label = QLabel(get_ipk_lang('19').format('', ''))
                page_layout.addWidget(self.error_label)
            case self.PAGE_finish_nochanges:
                # 第九页：完成（无变化）
                page_layout.addWidget(QLabel(get_ipk_lang('17')))
        
        page_layout.addStretch(1) # 居上显示
        return page_widget
    
    def copy_error(self):
        '''复制错误信息到剪贴板'''
        pyperclip.copy(self.error_label.text())
        MessageBox.information(self, get_ipk_lang('1a'), get_ipk_lang('1b'))
    
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
        self.template_combo.setCurrentText(get_ipk_lang('11'))

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
        self.template_combo.setCurrentText(get_ipk_lang('11'))

    @Slot(str)
    def apply_template(self, template_name):
        '''应用选择的模板'''
        if template_name == get_ipk_lang('11'):
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
            
        # 复制错误
        if self.current_page == self.PAGE_error:
            self.copy_error_btn.setVisible(True)
        else:
            self.copy_error_btn.setVisible(False)
            
        if self.current_page == self.PAGE_install:
            self.next_btn.setVisible(False)
            self.prev_btn.setVisible(False)
            self.cancel_btn.setVisible(False)
            
            if is_ipk:
                self.install_ipk()
            else:
                self.install()
        
        if is_ipk:
            if self.PAGE_read_license <= self.current_page <= self.PAGE_set_link: # ipk模式跳过这些步骤
                self.on_next()
        else:
            if self.current_page == self.PAGE_set_components and not(has_package):
                self.set_page(self.PAGE_install)
            
    def set_status(self, status):
        '''设置状态栏'''
        self.install_status = status
        
    def install_ipk(self):
        '''ipk模式安装'''
        global package_name

        try:
            self.set_status(get_ipk_lang('2b'))
            if not self.changes:
                self.set_page(self.PAGE_finish_nochanges)
                return

            self.set_status(get_ipk_lang('2e'))
            remove = []
            add = []
            for comp in self.changes:
                if comp.startswith('-'):
                    remove.append(comp[1:])
                elif comp.startswith('+'):
                    add.append(comp[1:])
            
            self.set_status(get_ipk_lang('26'))
            package_name = list(set(package_name) - set(remove))
            package_name = package_name + add
            with open('./packages.json', 'w', encoding='utf-8') as f:
                json.dump(package_name, f)

            self.set_status(get_ipk_lang('27'))
            for comp in add:
                extract_zip(get_resource_path('packages', f'{comp}.zip'), f'extensions/{comp}')

            for comp in remove:
                rmtree(f'extensions/{comp}', ignore_errors=True)

            self.set_page(self.PAGE_finish)
        except Exception:
            error_stack = traceback.format_exc()
            self.error_label.setText(get_ipk_lang('19').format(self.install_status, error_stack))
            self.set_page(self.PAGE_error)
    
    def install(self):
        '''安装'''
        try:
            self.set_status(get_ipk_lang('2b'))
            install_path = Path.cwd()
            
            if has_package:
                self.set_status(get_ipk_lang('26'))
                with open(fr'{install_path}\packages.json', 'w', encoding='utf-8') as f:
                    json.dump(package_id_list, f)
                
                self.set_status(get_ipk_lang('27'))
                for i in package_id_list:
                    if i == 'xystudio.clickmouse':
                        continue
                    extract_zip(get_resource_path('packages', f'{i}.zip'), f'extensions/{i}/')
            else:
                self.set_status(get_ipk_lang('27'))
                with open(fr'{install_path}\packages.json', 'w', encoding='utf-8') as f:
                    json.dump(["xystudio.clickmouse"], f)
            
            try:
                os.mkdir('extensions')
            except:
                pass    
                
            # 卸载功能
            self.set_status(get_ipk_lang('28'))
            key = winreg.CreateKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\clickmouse'
            )
            winreg.SetValue(key, '', winreg.REG_SZ, fr'{install_path}\main.exe')
            winreg.SetValueEx(key, 'Path', 0, winreg.REG_SZ, f'{install_path}')
            winreg.CloseKey(key)

            self.set_status(get_ipk_lang('29'))
            uninstall_key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickmouse')
            winreg.SetValueEx(uninstall_key, 'DisplayName', 0, winreg.REG_SZ, 'clickmouse')
            winreg.SetValueEx(uninstall_key, 'Publisher', 0, winreg.REG_SZ, f'xystudio')
            winreg.SetValueEx(uninstall_key, 'InstallLocation', 0, winreg.REG_SZ, f'{install_path}')
            winreg.SetValueEx(uninstall_key, 'UninstallString', 0, winreg.REG_SZ, fr'cmd /k echo 前往{install_path}\uninstall.exe以进行操作')
            winreg.SetValueEx(uninstall_key, 'ModifyPath', 0, winreg.REG_SZ, fr'cmd /k echo 前往{install_path}\install_pack.exe以进行操作')
            winreg.SetValueEx(uninstall_key, 'RepairPath', 0, winreg.REG_SZ, fr'cmd /k echo 前往{install_path}\repair.exe以进行操作')
            with open(get_resource_path('versions.json'), 'r', encoding='utf-8') as f:
                version = json.load(f)['clickmouse']
            winreg.SetValueEx(uninstall_key, 'DisplayVersion', 0, winreg.REG_SZ, version)

            winreg.SetValueEx(uninstall_key, 'EstimatedSize', 0, winreg.REG_DWORD, int(get_dir_size_for_reg(install_path)))
            winreg.SetValueEx(uninstall_key, 'URLInfoAbout', 0, winreg.REG_SZ, 'https://www.github.com/xystudiocode/pyclickmouse')
            winreg.SetValueEx(uninstall_key, 'DisplayIcon', 0, winreg.REG_SZ, fr'{install_path}\res\icons\clickmouse\icon.ico')
            
            winreg.SetValueEx(uninstall_key, 'RegOwner', 0, winreg.REG_SZ, 'xystudio')
            winreg.SetValueEx(uninstall_key, 'RegCompany', 0, winreg.REG_SZ, 'xystudio')
            winreg.SetValueEx(uninstall_key, 'ProductID', 0, winreg.REG_SZ, '40')
            winreg.SetValueEx(uninstall_key, 'Comments', 0, winreg.REG_SZ, 'Clickmouse')

            winreg.CloseKey(uninstall_key)

            self.set_status(get_ipk_lang('2a'))
            start_menu_path = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start menu', 'Programs', 'Clickmouse')
            if self.create_start_menu_shortcut:
                try:
                    os.mkdir(start_menu_path)
                except:
                    pass
                create_shortcut(os.path.join(start_menu_path, 'ClickMouse.lnk'), fr'{install_path}\main.exe', 'Clickmouse')
                create_shortcut(os.path.join(start_menu_path, 'Uninstall clickmouse.lnk'), fr'{install_path}\uninstall.exe', 'Uninstall clickmouse')
                create_shortcut(os.path.join(start_menu_path, 'Repair clickmouse.lnk'), fr'{install_path}\repair.exe', 'Repair clickmouse')
            if self.create_desktop_shortcut:
                create_shortcut(fr'{os.path.expanduser('~')}\Desktop\clickmouse.lnk', fr'{install_path}\main.exe', 'clickmouse')
            self.set_page(self.PAGE_finish)
        except Exception:
            error_stack = traceback.format_exc()
            self.error_label.setText(get_ipk_lang('19').format(self.install_status, error_stack))
            self.set_page(self.PAGE_error)
            
    def cancel(self):
        '''取消安装'''
        self.set_page(self.PAGE_cancel)

    def on_next(self):
        if self.current_page == self.PAGE_set_components:
            # 第四页：提示
            if is_ipk:
                self.changes = get_list_diff(self.all_packages_name, self.selected_components)
                
                message = MessageBox.question(
                    self,
                    get_ipk_lang('1a'),
                    get_ipk_lang('24').format('\n'.join(self.changes if self.changes else [get_ipk_lang('2f')])),
                MessageButtonTemplate.YESNO,
                )
                
                for i in packages_info:
                    if get_lang(i['package_name_index'], source=package_langs) in self.selected_components:
                        package_id_list.append(i['package_name'])
                        
                for i in packages_source:
                    select_package_id.append(i['package_name'])
                    
                self.changes = get_list_diff(select_package_id, package_id_list)

                if message == 3:
                    return
            else:
                message =QMessageBox.question(
                    self,
                    get_ipk_lang('1a'),
                    get_ipk_lang('1c').format('\n'.join(self.selected_components), get_ipk_lang('2c') if self.create_desktop_shortcut else '', get_ipk_lang('2d') if self.create_start_menu_shortcut else ''),
                QMessageBox.Yes | QMessageBox.No,
                )
                for i in packages_info:
                    if get_lang(i['package_name_index'], source=package_langs, lang_id=system_lang) in self.selected_components:
                        package_id_list.append(i['package_name'])
                if message == QMessageBox.No:
                    return
        super().on_next()
        
    def on_prev(self):
        if self.current_page == self.PAGE_set_components and is_ipk:
            # 第四页ipk：回滚要跳跃
            self.set_page(self.PAGE_hello)
        
    def closeEvent(self, event):
        if self.current_page < self.PAGE_finish:
            event.ignore()
            self.cancel()
        elif self.current_page == self.PAGE_finish and not is_ipk:
            with open(data_path / 'first_run', 'w'):pass # 标记为第一次运行
            settings['select_lang'] = parse_system_language_to_lang_id()
            save_settings(settings)
            if self.run_clickmouse.isChecked():
                run_software('main.py', 'main.exe')
                event.accept()
        else:
            event.accept()

if __name__ == '__main__':
    from sharelibs import mem_id
    shared_memory = QSharedMemory(mem_id[2])
    if shared_memory.attach():
        # 已经有一个实例在运行
        sys.exit(2)
    shared_memory.create(1)
    
    is_running = any(list(map(lambda x: QSharedMemory(x).attach(), mem_id[3:4])))
    if is_running:
        # 已经有一个实例在运行
        sys.exit(2)

    import pyperclip
    from sharelibs import (get_lang, settings, get_inst_lang, get_icon, system_lang, parse_system_language_to_lang_id, run_software, get_resource_path, is_admin, get_init_lang, run_as_admin)
    import win32com.client
    import winreg
    import zipfile
    from shutil import rmtree
    import traceback
    from uiStyles import styles, maps, UCheckBox
    import os
    from pathlib import Path
    import json
    
    # 系统api
    import ctypes
    from ctypes import wintypes
        
    is_ipk = '--ipk' in app.arguments()
    get_ipk_lang = get_inst_lang if is_ipk else get_init_lang
    
    # Windows API常量
    DWMWA_USE_IMMERSIVE = 20
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWM_WINDOW_CORNER_PREFERENCE = 33
    DWMWCP_ROUND = 2
    DWMNCRP_ENABLED = 1
    
    with open(get_resource_path('langs', 'packages.json'), 'r', encoding='utf-8') as f:
        package_langs = json.load(f)

    with open(get_resource_path('package_info.json'), 'r', encoding='utf-8') as f:
        packages_info = json.load(f)
        
    try:
        packages_source = []
        with open('packages.json', 'r', encoding='utf-8') as f:
            package_name = json.load(f)
        
        for i in package_name:
            packages_source.append(import_package(i))
    except FileNotFoundError:
        if os.path.exists('data/first_run'):
            os.remove(Path('data', 'first_run'))
    
    packages = get_packages()
    
    icon = get_icon('init')
    
    package_id_list = []
    select_package_id = []
    
    getter = ColorGetter()
    
    if not is_ipk:
        software_reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\clickMouse'
        data_path = Path('data')
        if check_reg_key(software_reg_key):
            QMessageBox.critical(None, get_ipk_lang('1d'), get_ipk_lang('1e'))
            with open(data_path / 'first_run', 'w'):pass
            run_software('main.py', 'main.exe')
            sys.exit(1)

        if is_admin():
            print('run as admin')
            is_running = any(list(map(lambda x: QSharedMemory(x).attach(), mem_id[3:4])))
            if is_running:
                # 已经有一个实例在运行
                sys.exit(2)

            has_package = os.path.exists(get_resource_path('packages'))
            if not has_package:
                QMessageBox.warning(None, get_ipk_lang('1d'), get_ipk_lang('1f'))

            package_id_list = []
            select_package_id = []
        else:
            QMessageBox.critical(None, get_init_lang('1d'), get_init_lang('20'))
            sys.exit(1)
    window = InstallWindow()
    window.show()
    sys.exit(app.exec())
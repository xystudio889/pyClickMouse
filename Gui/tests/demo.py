import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *

class CheckBoxDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('QCheckBox 颜色设置演示')
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("选择勾选标记颜色：")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        
        # 颜色选择按钮
        colors_layout = QHBoxLayout()
        colors = {
            "红色": "#FF5252",
            "绿色": "#4CAF50", 
            "蓝色": "#2196F3",
            "橙色": "#FF9800",
            "紫色": "#9C27B0"
        }
        
        self.checkbox = QCheckBox("这是一个测试复选框")
        self.checkbox.setStyleSheet(self.get_style_sheet("#2196F3"))
        
        for color_name, color_code in colors.items():
            btn = QPushButton(color_name)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_code};
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background-color: {self.lighten_color(color_code)};
                }}
            """)
            btn.clicked.connect(lambda checked, c=color_code: self.change_checkbox_color(c))
            colors_layout.addWidget(btn)
        
        layout.addLayout(colors_layout)
        layout.addSpacing(20)
        layout.addWidget(self.checkbox)
        
        # 添加更多示例
        layout.addSpacing(30)
        layout.addWidget(QLabel("更多样式示例："))
        
        # 样式1：圆角复选框
        checkbox1 = QCheckBox("圆角蓝色复选框")
        checkbox1.setStyleSheet("""
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border: 2px solid #888;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 2px solid #1976D2;
            }
        """)
        
        # 样式2：渐变复选框
        checkbox2 = QCheckBox("渐变紫色复选框")
        checkbox2.setStyleSheet("""
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #999;
            }
            QCheckBox::indicator:checked {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #9C27B0, stop:1 #7B1FA2
                );
                border: 1px solid #6A1B9A;
            }
        """)
        
        layout.addWidget(checkbox1)
        layout.addWidget(checkbox2)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def get_style_sheet(self, color):
        """生成样式表"""
        lighter = self.lighten_color(color)
        return f"""
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 3px;
                border: 2px solid #888;
            }}
            QCheckBox::indicator:checked {{
                background-color: {color};
                border: 2px solid {lighter};
            }}
            QCheckBox::indicator:hover {{
                border: 2px solid #666;
            }}
        """
    
    def lighten_color(self, hex_color, amount=30):
        """使颜色变亮"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        lighter = tuple(min(255, c + amount) for c in rgb)
        return f'#{lighter[0]:02x}{lighter[1]:02x}{lighter[2]:02x}'
    
    def change_checkbox_color(self, color):
        """改变复选框颜色"""
        self.checkbox.setStyleSheet(self.get_style_sheet(color))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = CheckBoxDemo()
    demo.show()
    sys.exit(app.exec())
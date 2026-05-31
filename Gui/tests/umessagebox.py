from PySide6.QtWidgets import QApplication, QMessageBox, QWidget
import sys

class MessageButtonTemplate:
    YES = 0b1
    NO = 0b10
    OK = 0b100
    CANCEL = 0b1000
    YESNO = YES | NO
    OKCANCEL = OK | CANCEL

class CustonMessageButton:
    def __init__(self, text, role):
        self.text = text
        self.role = role

class UMessageBox(QMessageBox):
    @staticmethod
    def new_msg(parent, 
                title: str, 
                text: str, 
                icon: QMessageBox.Icon, 
                buttons: MessageButtonTemplate = MessageButtonTemplate.OK,
                defaultButton: MessageButtonTemplate = MessageButtonTemplate.OK):
        
        msg_box = QMessageBox(icon, title, text, buttons=QMessageBox.NoButton, parent=parent)
        
        default_btn = None
        
        # 虽然下面的规则匹配有点奇怪，但是为了显示整齐所以要这样写
        if isinstance(buttons, int):
            if buttons & MessageButtonTemplate.YES:
                btn = msg_box.addButton('是', QMessageBox.YesRole)
                if defaultButton == MessageButtonTemplate.YES:
                    default_btn = btn
            
            if buttons & MessageButtonTemplate.NO:
                btn = msg_box.addButton('否', QMessageBox.AcceptRole)
                if defaultButton == MessageButtonTemplate.NO:
                    default_btn = btn
            
            if buttons & MessageButtonTemplate.OK:
                btn = msg_box.addButton('确定', QMessageBox.NoRole)
                if defaultButton == MessageButtonTemplate.OK:
                    default_btn = btn
            
            if buttons & MessageButtonTemplate.CANCEL:
                btn = msg_box.addButton('取消', QMessageBox.RejectRole)
                if defaultButton == MessageButtonTemplate.CANCEL:
                    default_btn = btn
        elif isinstance(buttons, CustonMessageButton):
            btn = msg_box.addButton(buttons.text, buttons.role)
            if defaultButton == buttons.role:
                default_btn = btn
        elif isinstance(buttons, list):
            for button in buttons:
                if isinstance(button, CustonMessageButton):
                    btn = msg_box.addButton(button.text, button.role)
                    if defaultButton == button.role:
                        default_btn = btn
                else:
                    raise ValueError('buttons must be a list of CustonMessageButton') # 报错
        else:
            raise ValueError('buttons must be a int or a list of CustonMessageButton') # 报错
        
        if default_btn:
            msg_box.setDefaultButton(default_btn)

        return msg_box
    
    @classmethod
    def warning(cls, parent, title: str, text: str, buttons: MessageButtonTemplate = MessageButtonTemplate.OK, defaultButton: MessageButtonTemplate = MessageButtonTemplate.OK):
        msg_box = cls.new_msg(parent, title, text, QMessageBox.Icon.Warning, buttons, defaultButton)
        return msg_box.exec()

    @classmethod
    def critical(cls, parent, title: str, text: str, buttons: MessageButtonTemplate = MessageButtonTemplate.OK, defaultButton: MessageButtonTemplate = MessageButtonTemplate.OK):
        msg_box = cls.new_msg(parent, title, text, QMessageBox.Icon.Critical, buttons, defaultButton)
        return msg_box.exec()
    
    @classmethod
    def information(cls, parent, title: str, text: str, buttons: MessageButtonTemplate = MessageButtonTemplate.OK, defaultButton: MessageButtonTemplate = MessageButtonTemplate.OK):
        msg_box = cls.new_msg(parent, title, text, QMessageBox.Icon.Information, buttons, defaultButton)
        return msg_box.exec()

    @classmethod
    def question(cls, parent, title: str, text: str, buttons: MessageButtonTemplate = MessageButtonTemplate.YESNO, defaultButton: MessageButtonTemplate = MessageButtonTemplate.YES):
        msg_box = cls.new_msg(parent, title, text, QMessageBox.Icon.Question, buttons, defaultButton)
        return msg_box.exec()
    
class Window(QWidget):
    def __init__(self):
        super().__init__()

def umessagebox():
    app = QApplication(sys.argv)
    window = Window()
    msg_box = UMessageBox.question(None, '测试', '你喜欢这个软件吗？', buttons=[CustonMessageButton('好', QMessageBox.YesRole), CustonMessageButton('不喜欢', QMessageBox.NoRole)])
    print(msg_box)
    msg_box = UMessageBox.question(None, '测试', '你喜欢这个软件吗？', buttons=MessageButtonTemplate.YESNO, defaultButton=MessageButtonTemplate.YES)
    print(msg_box)
    msg_box = UMessageBox.question(None, '测试', '你喜欢这个软件吗？', buttons=MessageButtonTemplate.OKCANCEL, defaultButton=MessageButtonTemplate.YES)
    print(msg_box)
    window.show()
    app.exec()
    
if __name__ == '__main__':
    umessagebox()
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QTextEdit, QColorDialog, QFontDialog,
                            QHBoxLayout, QLabel, QSpinBox, QComboBox, QMessageBox,
                            QToolBar, QStyle, QMenu, QColorDialog, QFontComboBox,
                            QToolButton, QFrame, QListWidget, QListWidgetItem,
                            QGridLayout, QFileDialog)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize, QPropertyAnimation, QEasingCurve, QEvent
from PyQt6.QtGui import QFont, QColor, QIcon, QAction, QPalette, QPixmap, QPainter, QTextDocument
from database import Database

class ColorButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.color = QColor('#FFFF99')
        self.setStyleSheet(f"""
            QToolButton {{
                background-color: {self.color.name()};
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }}
        """)
        
    def setColor(self, color):
        self.color = color
        self.setStyleSheet(f"""
            QToolButton {{
                background-color: {self.color.name()};
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }}
        """)

class FontPreviewWidget(QWidget):
    def __init__(self, font_name, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 预览文本
        preview = QLabel("你好")
        preview.setFont(QFont(font_name, 10))
        preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(preview)
        
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QLabel {
                color: #333333;
            }
        """)
        
    def enterEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background-color: #E0E0E0;
                border-radius: 3px;
            }
            QLabel {
                color: #333333;
            }
        """)
        
    def leaveEvent(self, event):
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            QLabel {
                color: #333333;
            }
        """)

class FontMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Popup | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        
        # 创建字体网格
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setSpacing(5)
        
        # 从数据库获取最近使用的字体
        self.db = Database()
        recent_fonts = self.db.get_recent_fonts()
        
        # 合并最近使用的字体和常用字体，去重
        self.common_fonts = ['微软雅黑', '宋体', '黑体', 'Arial', 'Times New Roman', 
                           '楷体', '仿宋', '幼圆', '方正舒体', '华文行楷']
        all_fonts = list(dict.fromkeys(recent_fonts + self.common_fonts))
        
        row = 0
        col = 0
        max_cols = 3  # 每行最多显示3个字体
        
        for font_name in all_fonts:
            font_widget = FontPreviewWidget(font_name)
            grid_layout.addWidget(font_widget, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加"更多"选项
        more_widget = QLabel("更多字体...")
        more_widget.setStyleSheet("""
            QLabel {
                color: #666666;
                padding: 5px;
                background-color: #F5F5F5;
                border-radius: 3px;
            }
            QLabel:hover {
                background-color: #E0E0E0;
            }
        """)
        more_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        more_widget.mousePressEvent = lambda event: self.show_more_fonts()
        grid_layout.addWidget(more_widget, row, col)
        
        # 添加字体网格到主布局
        main_layout.addWidget(grid_widget)
        
        # 设置菜单大小
        self.setFixedWidth(300)
        self.setFixedHeight(300)
        
    def show_more_fonts(self):
        font, ok = QFontDialog.getFont(QFont(), self)
        if ok:
            # 保存到最近使用的字体
            self.db.add_recent_font(font.family())
            # 通知父窗口更新字体
            if self.parent():
                self.parent().handle_font_selection(font.family())

class FontSizeMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Popup | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        
        # 创建字体大小调节区域
        size_widget = QWidget()
        size_layout = QHBoxLayout(size_widget)
        size_layout.setContentsMargins(0, 0, 0, 0)
        
        # 减小字体按钮
        decrease_btn = QToolButton()
        decrease_btn.setText('-')
        decrease_btn.setFixedSize(20, 20)
        decrease_btn.clicked.connect(lambda: self.adjust_font_size(-1))
        
        # 字体大小显示
        self.size_label = QLabel('10')
        self.size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.size_label.setFixedWidth(30)
        
        # 增大字体按钮
        increase_btn = QToolButton()
        increase_btn.setText('+')
        increase_btn.setFixedSize(20, 20)
        increase_btn.clicked.connect(lambda: self.adjust_font_size(1))
        
        size_layout.addWidget(decrease_btn)
        size_layout.addWidget(self.size_label)
        size_layout.addWidget(increase_btn)
        
        # 添加字体大小调节区域到主布局
        main_layout.addWidget(size_widget)
        
        # 设置菜单大小
        self.setFixedWidth(100)
        self.setFixedHeight(50)
        
    def adjust_font_size(self, delta):
        current_size = int(self.size_label.text())
        new_size = max(8, min(72, current_size + delta))
        self.size_label.setText(str(new_size))
        
        # 更新字体大小
        if self.parent():
            self.parent().handle_font_size_change(new_size)

class TextColorMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Popup | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        
        # 创建颜色网格
        color_grid = QWidget()
        color_layout = QGridLayout(color_grid)
        color_layout.setSpacing(2)
        
        # 添加常用文字颜色
        common_colors = [
            '#000000', '#333333', '#666666', '#999999', '#CCCCCC',
            '#FF0000', '#FF6600', '#FFCC00', '#00CC00', '#0066FF',
            '#6600FF', '#FF00FF', '#FF0066', '#00FFFF', '#66FF66'
        ]
        
        row = 0
        col = 0
        max_cols = 5
        
        for color in common_colors:
            color_btn = QPushButton()
            color_btn.setFixedSize(20, 20)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    border: 1px solid #666666;
                }}
            """)
            color_btn.clicked.connect(lambda checked, c=color: self.apply_color(c))
            color_layout.addWidget(color_btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加更多选项
        more_btn = QPushButton("更多...")
        more_btn.clicked.connect(self.show_color_dialog)
        color_layout.addWidget(more_btn, row, col)
        
        main_layout.addWidget(color_grid)
        
        # 设置菜单大小
        self.setFixedWidth(150)
        self.setFixedHeight(150)
        
    def apply_color(self, color):
        if self.parent():
            self.parent().text_color_btn.setColor(QColor(color))
            self.parent().text_edit.setTextColor(QColor(color))
        self.close()
        
    def show_color_dialog(self):
        if self.parent():
            color = QColorDialog.getColor(self.parent().text_color_btn.color, self)
            if color.isValid():
                self.apply_color(color.name())
        self.close()

class StickyNote(QWidget):
    def __init__(self, parent=None, note_id=None, background_image=None):
        super().__init__(None)
        # 初始化基本属性
        self.note_id = note_id
        self.parent_control = parent
        self.is_top_most = False
        self.background_image = background_image
        self.resize_handle_size = 10
        self.is_resizing = False
        self.resize_start_pos = None
        self.resize_start_geometry = None
        self.control_bar_visible = False
        self.top_bar_visible = False
        self.drag_start_pos = None
        self.is_dragging = False
        
        # 初始化字体相关属性
        self.min_font_size = 8  # 最小字体大小
        self.max_font_size = 72  # 最大字体大小
        self.default_font_size = 12  # 默认字体大小
        
        # 初始化便签大小限制
        self.min_width = 200  # 最小宽度
        self.min_height = 150  # 最小高度
        self.max_width = 800  # 最大宽度
        self.max_height = 600  # 最大高度
        
        # 初始化边距设置
        self.text_margin = 20  # 文本边距
        self.vertical_padding = 40  # 垂直方向额外padding
        self.horizontal_padding = 30  # 水平方向额外padding
        
        # 初始化UI
        self.initUI()

    def initUI(self):
        # 设置窗口基本属性
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(0)
        
        # 创建一个包装器widget来包含文本编辑器
        text_container = QWidget()
        text_container_layout = QVBoxLayout(text_container)
        text_container_layout.setContentsMargins(0, 0, 0, 0)
        text_container_layout.setSpacing(0)
        
        # 创建文本编辑器
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: transparent;
                border: none;
                padding: {self.text_margin}px;
            }}
        """)
        self.text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.text_edit.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.text_edit.installEventFilter(self)
        self.text_edit.textChanged.connect(self.adjust_font_size_to_fit)
        
        # 设置默认字体
        default_font = QFont('微软雅黑', self.default_font_size)
        self.text_edit.setFont(default_font)
        
        text_container_layout.addWidget(self.text_edit)
        
        # 创建顶部控制栏（初始隐藏）
        self.top_bar = QFrame()
        self.top_bar.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                margin-bottom: 2px;
            }
            QToolButton {
                border: none;
                padding: 2px;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
        """)
        top_layout = QHBoxLayout(self.top_bar)
        top_layout.setContentsMargins(2, 2, 2, 2)
        top_layout.setSpacing(2)
        
        # 添加关闭按钮到右上角
        close_button = QToolButton()
        close_button.setText('×')
        close_button.setFixedSize(20, 20)
        close_button.setToolTip("关闭")
        close_button.clicked.connect(self.close)
        close_button.setStyleSheet("""
            QToolButton {
                color: #666666;
                font-weight: bold;
            }
            QToolButton:hover {
                color: #FF0000;
                background-color: #E0E0E0;
            }
        """)
        
        # 对齐方式按钮
        align_left_btn = QToolButton()
        align_left_btn.setText('≡')
        align_left_btn.setFixedSize(20, 20)
        align_left_btn.setToolTip("左对齐")
        align_left_btn.clicked.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignLeft))
        
        align_center_btn = QToolButton()
        align_center_btn.setText('≡')
        align_center_btn.setFixedSize(20, 20)
        align_center_btn.setToolTip("居中对齐")
        align_center_btn.clicked.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignCenter))
        
        align_right_btn = QToolButton()
        align_right_btn.setText('≡')
        align_right_btn.setFixedSize(20, 20)
        align_right_btn.setToolTip("右对齐")
        align_right_btn.clicked.connect(lambda: self.set_alignment(Qt.AlignmentFlag.AlignRight))
        
        # 设置按钮样式
        for btn in [align_left_btn, align_center_btn, align_right_btn]:
            btn.setStyleSheet("""
                QToolButton {
                    border: none;
                    padding: 2px;
                    border-radius: 2px;
                    font-size: 14px;
                }
                QToolButton:hover {
                    background-color: #E0E0E0;
                }
                QToolButton:checked {
                    background-color: #E0E0E0;
                }
            """)
            btn.setCheckable(True)
        
        # 添加背景图片按钮
        bg_image_btn = QToolButton()
        bg_image_btn.setText('🖼️')
        bg_image_btn.setFixedSize(20, 20)
        bg_image_btn.setToolTip("更换背景")
        bg_image_btn.clicked.connect(self.choose_background)
        
        # 添加缩放选项按钮
        scale_btn = QToolButton()
        scale_btn.setText('📏')
        scale_btn.setFixedSize(20, 20)
        scale_btn.setToolTip("缩放选项")
        scale_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        
        # 创建缩放菜单
        scale_menu = QMenu(scale_btn)
        scale_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
        """)
        
        # 添加缩放选项
        scale_actions = {
            "适应窗口": lambda: self.scale_background(Qt.AspectRatioMode.KeepAspectRatio),
            "拉伸填充": lambda: self.scale_background(Qt.AspectRatioMode.IgnoreAspectRatio),
            "原始大小": lambda: self.scale_background(None),
            "适应宽度": lambda: self.scale_background(Qt.AspectRatioMode.KeepAspectRatio, True),
            "适应高度": lambda: self.scale_background(Qt.AspectRatioMode.KeepAspectRatio, False)
        }
        
        for text, action in scale_actions.items():
            menu_action = QAction(text, scale_menu)
            menu_action.triggered.connect(action)
            scale_menu.addAction(menu_action)
        
        scale_btn.setMenu(scale_menu)
        
        # 添加控件到顶部栏
        top_layout.addWidget(align_left_btn)
        top_layout.addWidget(align_center_btn)
        top_layout.addWidget(align_right_btn)
        top_layout.addWidget(bg_image_btn)
        top_layout.addWidget(scale_btn)
        top_layout.addStretch()
        top_layout.addWidget(close_button)
        
        # 创建底部控制栏（初始隐藏）
        self.control_bar = QFrame()
        self.control_bar.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                margin-top: 2px;
            }
            QToolButton {
                border: none;
                padding: 2px;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
        """)
        control_layout = QHBoxLayout(self.control_bar)
        control_layout.setContentsMargins(2, 2, 2, 2)
        control_layout.setSpacing(2)
        
        # 字体选择按钮
        font_btn = QToolButton()
        font_btn.setText('A')
        font_btn.setFixedSize(20, 20)
        font_btn.setToolTip("选择字体")
        font_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.font_menu = FontMenu(self)
        font_btn.setMenu(self.font_menu)
        
        # 字体大小按钮
        font_size_btn = QToolButton()
        font_size_btn.setText('Aa')
        font_size_btn.setFixedSize(20, 20)
        font_size_btn.setToolTip("字体大小")
        font_size_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.font_size_menu = FontSizeMenu(self)
        font_size_btn.setMenu(self.font_size_menu)
        
        # 文字颜色选择
        self.text_color_btn = ColorButton()
        self.text_color_btn.setColor(QColor('#000000'))
        self.text_color_btn.setFixedSize(20, 20)
        self.text_color_btn.setToolTip("文字颜色")
        self.text_color_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.text_color_menu = TextColorMenu(self)
        self.text_color_btn.setMenu(self.text_color_menu)
        
        # 置顶按钮
        self.top_button = QToolButton()
        self.top_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
        self.top_button.setFixedSize(20, 20)
        self.top_button.setToolTip("置顶")
        self.top_button.setStyleSheet("""
            QToolButton {
                border: none;
                padding: 2px;
                border-radius: 2px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
            }
            QToolButton:checked {
                background-color: #4CAF50;
                color: white;
            }
        """)
        self.top_button.setCheckable(True)
        self.top_button.clicked.connect(self.toggle_top_most)
        
        # 添加控件到控制栏
        control_layout.addWidget(font_btn)
        control_layout.addWidget(font_size_btn)
        control_layout.addWidget(self.text_color_btn)
        control_layout.addWidget(self.top_button)
        control_layout.addStretch()
        control_layout.addWidget(close_button)
        
        # 添加控件到主布局
        main_layout.addWidget(self.top_bar)
        main_layout.addWidget(text_container)
        main_layout.addWidget(self.control_bar)
        
        # 设置窗口大小和位置
        self.resize(300, 200)
        
        # 获取屏幕尺寸并随机放置便签
        screen = QApplication.primaryScreen().geometry()
        import random
        x = random.randint(50, max(50, screen.width() - self.width() - 50))
        y = random.randint(50, max(50, screen.height() - self.height() - 50))
        self.move(x, y)
        
        # 初始隐藏控制栏
        self.control_bar.hide()
        self.top_bar.hide()
        
        # 设置背景
        if self.background_image:
            self.set_background(self.background_image)
        else:
            self.set_default_background()
            
    def set_default_background(self):
        # 创建默认背景
        pixmap = QPixmap(self.size())
        pixmap.fill(QColor('#FFFF99'))  # 默认黄色背景
        self.set_background(pixmap)
        
    def set_background(self, image):
        if isinstance(image, str):
            pixmap = QPixmap(image)
        else:
            pixmap = image
            
        if not pixmap.isNull():
            # 保持原始比例
            if isinstance(image, str):  # 如果是从文件加载的图片
                # 调整窗口大小以适应图片
                self.resize(pixmap.size())
                self.background_image = pixmap
            else:  # 如果是默认背景或透明背景
                # 调整图片大小以适应窗口
                pixmap = pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.background_image = pixmap
            self.update()
            
    def choose_background(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            # 创建透明背景
            transparent_pixmap = QPixmap(self.size())
            transparent_pixmap.fill(Qt.GlobalColor.transparent)
            self.set_background(transparent_pixmap)
            
            # 加载并设置选择的背景图片
            self.set_background(file_name)
            
            # 更新文本编辑器的背景为透明
            self.text_edit.setStyleSheet("""
                QTextEdit {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
            """)
            
    def paintEvent(self, event):
        if self.background_image:
            painter = QPainter(self)
            # 计算居中位置
            x = (self.width() - self.background_image.width()) // 2
            y = (self.height() - self.background_image.height()) // 2
            painter.drawPixmap(x, y, self.background_image)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在调整大小的区域
            if self.is_in_resize_area(event.position().toPoint()):
                self.is_resizing = True
                self.resize_start_pos = event.position()
                self.resize_start_geometry = self.geometry()
            else:
                self.drag_start_pos = event.position()
                self.is_dragging = True
                # 显示控制栏
                if not self.control_bar_visible:
                    self.show_control_bar()
                if not self.top_bar_visible:
                    self.show_top_bar()
                    
    def mouseMoveEvent(self, event):
        if self.is_resizing:
            # 计算新的窗口大小
            delta = event.position() - self.resize_start_pos
            new_geometry = self.resize_start_geometry
            new_geometry.setWidth(max(100, new_geometry.width() + int(delta.x())))
            new_geometry.setHeight(max(100, new_geometry.height() + int(delta.y())))
            self.setGeometry(new_geometry)
            
            # 更新背景图片大小
            if self.background_image:
                self.set_background(self.background_image)
        elif self.is_dragging and self.drag_start_pos is not None:
            # 计算移动距离
            delta = event.position() - self.drag_start_pos
            new_pos = self.pos() + QPoint(int(delta.x()), int(delta.y()))
            
            # 获取屏幕尺寸
            screen = QApplication.primaryScreen().geometry()
            
            # 确保便签不会完全移出屏幕
            new_pos.setX(max(-self.width() + 50, min(new_pos.x(), screen.width() - 50)))
            new_pos.setY(max(-self.height() + 50, min(new_pos.y(), screen.height() - 50)))
            
            self.move(new_pos)
            
    def mouseReleaseEvent(self, event):
        self.is_dragging = False
        self.is_resizing = False
        self.drag_start_pos = None
        self.resize_start_pos = None
        self.resize_start_geometry = None
        
    def is_in_resize_area(self, pos):
        # 检查是否在右下角调整大小的区域
        return (pos.x() > self.width() - self.resize_handle_size and 
                pos.y() > self.height() - self.resize_handle_size)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.background_image:
            self.set_background(self.background_image)
        self.adjust_font_size_to_fit()
            
    def set_alignment(self, alignment):
        self.text_edit.setAlignment(alignment)
        # 更新按钮状态
        for btn in self.top_bar.findChildren(QToolButton):
            if btn.toolTip() == "左对齐" and alignment == Qt.AlignmentFlag.AlignLeft:
                btn.setChecked(True)
            elif btn.toolTip() == "居中对齐" and alignment == Qt.AlignmentFlag.AlignCenter:
                btn.setChecked(True)
            elif btn.toolTip() == "右对齐" and alignment == Qt.AlignmentFlag.AlignRight:
                btn.setChecked(True)
            else:
                btn.setChecked(False)
        
    def enterEvent(self, event):
        if not self.control_bar_visible:
            self.show_control_bar()
        if not self.top_bar_visible:
            self.show_top_bar()
            
    def leaveEvent(self, event):
        if self.control_bar_visible and not self.control_bar.underMouse() and not self.is_dragging:
            self.hide_control_bar()
        if self.top_bar_visible and not self.top_bar.underMouse() and not self.is_dragging:
            self.hide_top_bar()
            
    def show_control_bar(self):
        self.control_bar.show()
        self.control_bar_visible = True
        
    def hide_control_bar(self):
        self.control_bar.hide()
        self.control_bar_visible = False
        
    def show_top_bar(self):
        self.top_bar.show()
        self.top_bar_visible = True
        
    def hide_top_bar(self):
        self.top_bar.hide()
        self.top_bar_visible = False
        
    def handle_font_selection(self, font_name):
        # 保存到最近使用的字体
        self.db = Database()
        self.db.add_recent_font(font_name)
        
        # 更新字体
        current_font = self.text_edit.font()
        new_font = QFont(font_name, current_font.pointSize())
        self.text_edit.setFont(new_font)
        
        # 更新字体菜单
        self.font_menu = FontMenu(self)
        self.findChild(QToolButton).setMenu(self.font_menu)
        
    def choose_text_color(self):
        # 这个方法现在可以删除，因为已经不需要了
        pass
        
    def toggle_top_most(self):
        if self.is_top_most:
            # 取消置顶
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            self.is_top_most = False
            self.top_button.setChecked(False)
        else:
            # 设置置顶
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
            self.is_top_most = True
            self.top_button.setChecked(True)
        self.show()
        
    def restore_window_state(self):
        # 恢复窗口状态
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.is_top_most = False
        self.top_button.setChecked(False)
        self.show()
        
    def closeEvent(self, event):
        if self.parent_control:
            self.parent_control.remove_note(self)
        event.accept()

    def eventFilter(self, obj, event):
        if obj == self.text_edit:
            if event.type() == QEvent.Type.MouseButtonDblClick:
                # 如果是文本编辑器的双击事件，我们处理它
                if self.is_top_most:
                    self.toggle_top_most()
                    return True  # 事件已处理
        return super().eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event):
        # 双击便签的任何区域都会触发这个事件
        if self.is_top_most:
            self.toggle_top_most()
        # 不调用super().mouseDoubleClickEvent(event)，以防止事件继续传播

    def scale_background(self, mode, fit_width=False):
        if not self.background_image:
            return
            
        if mode is None:  # 原始大小
            self.resize(self.background_image.size())
        else:
            if fit_width:
                # 适应宽度
                new_width = self.width()
                new_height = int(self.background_image.height() * (new_width / self.background_image.width()))
                self.resize(new_width, new_height)
            else:
                # 适应高度
                new_height = self.height()
                new_width = int(self.background_image.width() * (new_height / self.background_image.height()))
                self.resize(new_width, new_height)
                
            # 缩放背景图片
            scaled_pixmap = self.background_image.scaled(
                self.size(),
                mode,
                Qt.TransformationMode.SmoothTransformation
            )
            self.background_image = scaled_pixmap
            self.update()

    def adjust_font_size_to_fit(self):
        # 获取当前文本内容
        text = self.text_edit.toPlainText()
        if not text:
            return

        # 获取当前字体
        current_font = self.text_edit.font()
        current_size = current_font.pointSize()
        
        # 获取文本编辑器的可用空间（考虑边距）
        available_width = self.text_edit.width() - (self.text_margin * 2 + self.horizontal_padding)
        available_height = self.text_edit.height() - (self.text_margin * 2 + self.vertical_padding)
        
        # 创建临时QTextDocument来计算文本大小
        doc = QTextDocument()
        doc.setDefaultFont(current_font)
        doc.setPlainText(text)
        
        # 计算文本所需的大小
        text_width = doc.size().width()
        text_height = doc.size().height()
        
        # 如果文本大小超过可用空间，尝试调整便签大小
        if text_width > available_width or text_height > available_height:
            # 计算需要的新大小（加上边距）
            new_width = min(self.max_width, max(self.min_width, 
                int(text_width + self.text_margin * 2 + self.horizontal_padding)))
            new_height = min(self.max_height, max(self.min_height, 
                int(text_height + self.text_margin * 2 + self.vertical_padding)))
            
            # 获取当前窗口位置
            current_pos = self.pos()
            
            # 计算新的窗口位置（保持左上角不变）
            new_x = current_pos.x()
            new_y = current_pos.y()
            
            # 调整窗口大小
            self.resize(new_width, new_height)
            
            # 更新背景图片
            if self.background_image:
                self.set_background(self.background_image)
            
            # 重新计算可用空间
            available_width = self.text_edit.width() - (self.text_margin * 2 + self.horizontal_padding)
            available_height = self.text_edit.height() - (self.text_margin * 2 + self.vertical_padding)
        
        # 使用二分查找合适的字体大小
        min_size = self.min_font_size
        max_size = self.max_font_size
        best_size = current_size
        
        while min_size <= max_size:
            mid_size = (min_size + max_size) // 2
            test_font = QFont(current_font)
            test_font.setPointSize(mid_size)
            doc.setDefaultFont(test_font)
            doc.setPlainText(text)
            
            # 检查文本是否适应可用空间
            if doc.size().width() <= available_width and doc.size().height() <= available_height:
                best_size = mid_size
                min_size = mid_size + 1
            else:
                max_size = mid_size - 1
        
        # 如果找到的字体大小与当前不同，则更新
        if best_size != current_size:
            new_font = QFont(current_font)
            new_font.setPointSize(best_size)
            self.text_edit.setFont(new_font)
            
            # 更新字体大小菜单的显示
            if hasattr(self, 'font_size_menu'):
                self.font_size_menu.size_label.setText(str(best_size))

    def handle_font_size_change(self, size):
        # 更新字体大小
        current_font = self.text_edit.font()
        new_font = QFont(current_font.family(), size)
        self.text_edit.setFont(new_font)
        self.adjust_font_size_to_fit()

class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.notes = []
        self.db = Database()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('便签控制面板')
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # 创建工具栏
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setIconSize(QSize(16, 16))
        
        # 新建便签按钮
        new_note_action = QAction('新建便签', self)
        new_note_action.triggered.connect(self.create_new_note)
        toolbar.addAction(new_note_action)
        
        # 添加分隔符
        toolbar.addSeparator()
        
        # 字体选择按钮
        font_btn = QToolButton()
        font_btn.setText('字体')
        font_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.font_menu = FontMenu()
        font_btn.setMenu(self.font_menu)
        toolbar.addWidget(font_btn)
        
        # 背景颜色按钮
        bg_color_btn = QToolButton()
        bg_color_btn.setText('背景')
        bg_color_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        bg_color_menu = QMenu(bg_color_btn)
        
        # 创建颜色网格
        color_grid = QWidget()
        color_layout = QGridLayout(color_grid)
        color_layout.setSpacing(2)
        
        # 添加常用颜色
        common_colors = [
            '#FFFF99', '#FFFFFF', '#FFE4E1', '#E0FFFF', '#F0FFF0',
            '#FFB6C1', '#87CEEB', '#98FB98', '#DDA0DD', '#F0E68C'
        ]
        
        row = 0
        col = 0
        max_cols = 5
        
        for color in common_colors:
            color_btn = QPushButton()
            color_btn.setFixedSize(20, 20)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    border: 1px solid #CCCCCC;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    border: 1px solid #666666;
                }}
            """)
            color_btn.clicked.connect(lambda checked, c=color: self.apply_bg_color(c))
            color_layout.addWidget(color_btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # 添加更多选项
        more_btn = QPushButton("更多...")
        more_btn.clicked.connect(self.choose_bg_color)
        color_layout.addWidget(more_btn, row, col)
        
        bg_color_menu.setLayout(QVBoxLayout())
        bg_color_menu.layout().addWidget(color_grid)
        bg_color_btn.setMenu(bg_color_menu)
        toolbar.addWidget(bg_color_btn)
        
        # 设置工具栏样式
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #F0F0F0;
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                spacing: 3px;
                padding: 2px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 2px;
                padding: 2px 5px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #E0E0E0;
                border: 1px solid #CCCCCC;
            }
            QMenu {
                background-color: white;
                border: 1px solid #CCCCCC;
            }
            QMenu::item {
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #E0E0E0;
            }
        """)
        
        # 添加工具栏到主布局
        main_layout.addWidget(toolbar)
        
        # 保存当前样式设置
        self.current_font = QFont('Arial', 12)
        self.current_bg_color = '#FFFF99'
        self.current_text_color = '#000000'
        
        # 设置窗口大小
        self.resize(300, toolbar.sizeHint().height() + 10)
        
        # 将窗口移动到屏幕顶部中央
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, 0)
        
    def create_new_note(self):
        try:
            note = StickyNote(self)
            note.text_edit.setFont(self.current_font)
            note.text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {self.current_bg_color};
                    color: {self.current_text_color};
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            note.show()
            note.raise_()
            note.activateWindow()
            self.notes.append(note)
            print(f"便签已创建: {len(self.notes)}个")
        except Exception as e:
            print(f"创建便签时出错: {str(e)}")
            
    def remove_note(self, note):
        if note in self.notes:
            self.notes.remove(note)
            print(f"便签已删除，剩余: {len(self.notes)}个")
            
    def apply_font(self, font_name):
        font = QFont(font_name)
        self.current_font = font
        for note in self.notes:
            note.text_edit.setFont(font)
            
    def choose_font(self):
        font, ok = QFontDialog.getFont(self.current_font, self)
        if ok:
            self.current_font = font
            for note in self.notes:
                note.text_edit.setFont(font)
                
    def apply_bg_color(self, color):
        self.current_bg_color = color
        for note in self.notes:
            note.text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {color};
                    color: {self.current_text_color};
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    padding: 5px;
                }}
            """)
            
    def choose_bg_color(self):
        color = QColorDialog.getColor(QColor(self.current_bg_color))
        if color.isValid():
            self.current_bg_color = color.name()
            for note in self.notes:
                note.text_edit.setStyleSheet(f"""
                    QTextEdit {{
                        background-color: {self.current_bg_color};
                        color: {self.current_text_color};
                        border: 1px solid #CCCCCC;
                        border-radius: 5px;
                        padding: 5px;
                    }}
                """)

    def create_color_icon(self, color):
        pixmap = QPixmap(16, 16)
        pixmap.fill(QColor(color))
        return QIcon(pixmap)

    def closeEvent(self, event):
        # 关闭所有便签
        for note in self.notes[:]:  # 使用切片创建副本以避免在迭代时修改列表
            note.close()
        # 接受关闭事件，程序将退出
        event.accept()
        # 强制退出应用程序
        QApplication.quit()

def main():
    app = QApplication(sys.argv)
    
    # 创建控制面板实例
    control_panel = ControlPanel()
    control_panel.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 
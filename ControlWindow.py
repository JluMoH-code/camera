import sys
import cv2
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from VideoWidget import VideoWidget
from StyledButton import StyledButton

from CameraCommandManager import CameraCommandManager
from ThreadedCamera import ThreadedCamera

commandManager = CameraCommandManager()

class ControlWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("videoWidget")
        
        self.current_pitch = 0
        self.current_yaw = 0
        self.step = 10
        self.cap = None
        
        # Инициализация стилей и UI
        self.init_ui()
        self.load_styles()
        self.init_camera()
        
    def load_styles(self):
        try:
            path = os.path.join(os.path.dirname(__file__), 'styles.qss')
            with open(path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Ошибка загрузки стилей: {str(e)}")
        
    def init_ui(self):
        self.setWindowTitle("Camera Controller")
        self.setMinimumSize(1280, 720)
        
        # Создание основных виджетов
        self.create_widgets()
        self.create_layout()
        self.create_menu()
        self.setup_connections()
        
    def create_widgets(self):
        # Виджет видео
        self.video_widget = VideoWidget()
        
        # Основные кнопки управления
        self.btn_lock = StyledButton("Lock Mode (L)")
        self.btn_fpv = StyledButton("FPV Mode (F)")
        self.btn_follow = StyledButton("Follow Mode (O)")
        self.btn_center = StyledButton("Auto Center (C)")
        self.btn_capture = StyledButton("Take Picture (P)")
        
        # Управление движением
        self.btn_up = StyledButton("Up (W)")
        self.btn_down = StyledButton("Down (S)")
        self.btn_left = StyledButton("Left (A)")
        self.btn_right = StyledButton("Right (D)")
        
        # Управление зумом
        self.btn_zoom_in = StyledButton("Zoom + (Z)")
        self.btn_zoom_out = StyledButton("Zoom - (X)")
        
        # Слайдеры
        self.pitch_slider = QSlider(Qt.Horizontal)
        self.yaw_slider = QSlider(Qt.Horizontal)
        
        # Индикаторы
        self.status_label = QLabel("Статус: Не подключено")
        self.status_label.setObjectName("statusLabel")
        
    def create_layout(self):
        main_layout = QHBoxLayout()
        
        # Левая панель - видео
        video_frame = QVBoxLayout()
        video_title = QLabel("Камера")
        video_title.setObjectName("title")
        video_frame.addWidget(video_title)
        video_frame.addWidget(self.video_widget)
        main_layout.addLayout(video_frame, 70)
        
        # Правая панель - управление
        control_layout = QVBoxLayout()
        
        # Группа режимов
        mode_group = QGroupBox("Режимы работы")
        mode_grid = QGridLayout()
        mode_grid.addWidget(self.btn_lock, 0, 0)
        mode_grid.addWidget(self.btn_fpv, 0, 1)
        mode_grid.addWidget(self.btn_follow, 1, 0)
        mode_grid.addWidget(self.btn_center, 1, 1)
        mode_group.setLayout(mode_grid)
        
        # Группа управления движением
        move_group = QGroupBox("Управление движением")
        move_grid = QGridLayout()
        move_grid.addWidget(self.btn_up, 0, 1)
        move_grid.addWidget(self.btn_left, 1, 0)
        move_grid.addWidget(self.btn_right, 1, 2)
        move_grid.addWidget(self.btn_down, 2, 1)
        move_group.setLayout(move_grid)
        
        # Группа зума
        zoom_group = QGroupBox("Управление зумом")
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)
        zoom_group.setLayout(zoom_layout)
        
        # Сборка правой панели
        control_layout.addWidget(mode_group)
        control_layout.addWidget(move_group)
        control_layout.addWidget(zoom_group)
        control_layout.addWidget(self.status_label)
        
        main_layout.addLayout(control_layout, 30)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
    def setup_connections(self):
        # Подключение кнопок
        self.btn_lock.clicked.connect(lambda: self.send_base_command("lock-mode"))
        self.btn_fpv.clicked.connect(lambda: self.send_base_command("fpv-mode"))
        self.btn_follow.clicked.connect(lambda: self.send_base_command("follow-mode"))
        self.btn_center.clicked.connect(lambda: self.send_base_command("auto-centering"))
        self.btn_capture.clicked.connect(lambda: self.send_base_command("take-picture"))
        
        self.btn_up.clicked.connect(self.move_up)
        self.btn_down.clicked.connect(self.move_down)
        self.btn_left.clicked.connect(self.move_left)
        self.btn_right.clicked.connect(self.move_right)
        
        self.btn_zoom_in.clicked.connect(lambda: self.send_base_command("zoom-1"))
        self.btn_zoom_out.clicked.connect(lambda: self.send_base_command("zoom--1"))
        
        self.video_widget.retry_btn.clicked.connect(self.restart_camera)
        
        # Таймер обновления видео
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)
        
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Инструменты")
        exit_action = QAction("Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
       
    def restart_camera(self):
        try:
            if self.cap:
                self.cap.stop()
                self.cap = None
                
            self.video_widget.show_retry()
            self.status_label.setText("Статус: Попытка подключения...")
            
            QTimer.singleShot(0, self.init_camera)  
            
        except Exception as e:
            print(f"Ошибка перезапуска: {str(e)}")
            self.status_label.setText("Статус: Ошибка перезапуска")
        
    def init_camera(self):
        try:
            if self.cap:
                self.cap.stop()
                
            self.cap = ThreadedCamera("rtsp://192.168.144.25:8554/main.264", timeout=5).start()
            self.status_label.setText("Статус: Подключение к камере...")
            self.video_widget.show_video()
            
            self.check_connection()
            
            QTimer.singleShot(1000, self.check_connection)
            
        except Exception as e:
            print(f"Ошибка: {str(e)}")
            self.status_label.setText("Статус: Ошибка подключения")
            self.video_widget.show_retry()
            
    def check_connection(self):
        if self.cap:
            if self.cap.connected:
                self.status_label.setText("Статус: Подключено")
                self.video_widget.show_video()
            else:
                self.status_label.setText("Статус: Соединение потеряно")
                self.video_widget.show_retry()
        else:
            self.status_label.setText("Статус: Нет соединения")
            self.video_widget.show_retry()
            QTimer.singleShot(1000, self.check_connection)
        
    def update_frame(self):
        if self.cap and self.cap.connected:
            try:
                img = self.cap.read()
                if img is not None:
                    img = cv2.resize(img, (1280, 720))
                    self.video_widget.update_image(img)
                    self.status_label.setText("Статус: Подключено")
                else:
                    self.status_label.setText("Статус: Нет видеопотока")
                    self.video_widget.show_retry()
            except:
                self.status_label.setText("Статус: Ошибка получения кадра")
                self.video_widget.show_retry()
        else:
            self.status_label.setText("Статус: Не подключено")
            self.video_widget.show_retry()
            
    def keyPressEvent(self, event):
        key = event.key()
        
        if key == Qt.Key_L:
            self.send_base_command("lock-mode")
        elif key == Qt.Key_F:
            self.send_base_command("fpv-mode")
        elif key == Qt.Key_O:
            self.send_base_command("follow-mode")
        elif key == Qt.Key_W:
            self.move_up()
        elif key == Qt.Key_S:
            self.move_down()
        elif key == Qt.Key_A:
            self.move_left()
        elif key == Qt.Key_D:
            self.move_right()
        elif key == Qt.Key_G:
            print(commandManager.base_command("attitude-data"))
        elif key == Qt.Key_C:
            self.send_base_command("auto-centering")
        elif key == Qt.Key_Z:
            print(commandManager.base_command("zoom-1"))
        elif key == Qt.Key_X:
            print(commandManager.base_command("zoom--1"))
        elif key == Qt.Key_P:
            print(commandManager.base_command("take-picture"))
        elif key == Qt.Key_Q:
            self.close()
            
    def send_base_command(self, command):
        commandManager.base_command(command)
        
    def move_up(self):
        self.current_pitch -= self.step
        if self.current_pitch <= -90:
            self.current_pitch = -90
        self.update_position()
        
    def move_down(self):
        self.current_pitch += self.step
        if self.current_pitch >= 25:
            self.current_pitch = 25
        self.update_position()
        
    def move_left(self):
        self.current_yaw += self.step
        if self.current_yaw >= 135:
            self.current_yaw = 135
        self.update_position()
        
    def move_right(self):
        self.current_yaw -= self.step
        if self.current_yaw <= -135:
            self.current_yaw = -135
        self.update_position()
        
    def update_position(self):
        commandManager.rotate(self.current_yaw * 10, self.current_pitch * 10)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec_())
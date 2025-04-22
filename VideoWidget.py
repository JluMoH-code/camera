from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

class VideoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("videoWidget")  # Важно для применения стилей
        
        self.layout = QVBoxLayout(self)
        self.image_label = QLabel("Ожидание видео...", self)
        self.image_label.setObjectName("videoStatusLabel")  # ID для стиля
        self.image_label.setAlignment(Qt.AlignCenter)
        
        self.retry_btn = QPushButton("Запустить видео", self)
        self.retry_btn.setObjectName("retryButton")  # ID для стиля
        
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.retry_btn)
        self.retry_btn.hide()

        # Убраны все setStyleSheet из кода

    def show_video(self):
        self.image_label.setText("")
        self.retry_btn.hide()

    def show_retry(self):
        self.image_label.setText("Не удалось подключиться к камере")
        self.retry_btn.show()

    def update_image(self, cv_img):
        if cv_img is not None:
            ht, wd, ch = cv_img.shape
            bytes_per_line = ch * wd
            q_img = QImage(cv_img.data, wd, ht, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.image_label.setPixmap(QPixmap.fromImage(q_img))
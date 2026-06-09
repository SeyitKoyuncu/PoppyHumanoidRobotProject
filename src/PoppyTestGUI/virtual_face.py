from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QPen

class VirtualFace(QWidget):
    def __init__(self):
        super().__init__()
        self.emotion = 'neutral' 
        self.setMinimumSize(300, 200)

    def change_emotion(self, emotion):
        self.emotion = emotion
        self.update() 

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.black)
        
        pen = QPen(QColor(0, 255, 255))
        pen.setWidth(8)
        painter.setPen(pen)

        w = self.width()
        h = self.height()
        eye_w, eye_h = 60, 60
        left_eye_x, left_eye_y = (w // 3) - (eye_w // 2), (h // 2) - (eye_h // 2)
        right_eye_x, right_eye_y = (w * 2 // 3) - (eye_w // 2), (h // 2) - (eye_h // 2)

        if self.emotion == 'neutral':
            painter.drawEllipse(left_eye_x, left_eye_y, eye_w, eye_h)
            painter.drawEllipse(right_eye_x, right_eye_y, eye_w, eye_h)
        elif self.emotion == 'happy':
            painter.drawArc(left_eye_x, left_eye_y, eye_w, eye_h, 0 * 16, 180 * 16)
            painter.drawArc(right_eye_x, right_eye_y, eye_w, eye_h, 0 * 16, 180 * 16)
        elif self.emotion == 'angry':
            painter.drawEllipse(left_eye_x, left_eye_y, eye_w, eye_h)
            painter.drawEllipse(right_eye_x, right_eye_y, eye_w, eye_h)
            black_pen = QPen(Qt.black)
            black_pen.setWidth(20)
            painter.setPen(black_pen)
            painter.drawLine(left_eye_x - 10, left_eye_y - 10, left_eye_x + eye_w + 10, left_eye_y + 30)
            painter.drawLine(right_eye_x - 10, right_eye_y + 30, right_eye_x + eye_w + 10, right_eye_y - 10)
        elif self.emotion == 'sad':
            painter.drawArc(left_eye_x, left_eye_y - 20, eye_w, eye_h, 180 * 16, 180 * 16)
            painter.drawArc(right_eye_x, right_eye_y - 20, eye_w, eye_h, 180 * 16, 180 * 16)
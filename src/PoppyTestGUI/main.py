import sys
import os
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QRadioButton, QComboBox, 
                             QTextEdit, QLabel, QGroupBox)
                             
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.PoppyTestGUI.virtual_face import VirtualFace
from src.Controllers.RobotController import RobotController

class PoppyTesterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Start RobotController and pass the log_message function for logging
        self.controller = RobotController(log_callback=self.log_message)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Poppy Humanoid Control Center")
        self.resize(750, 600)

        main_widget = QWidget()
        main_layout = QHBoxLayout() 

        # Left panel for connection and motor controls
        left_panel = QVBoxLayout()

        mode_group = QGroupBox("Connection Mode")
        mode_layout = QHBoxLayout()
        self.radio_sim = QRadioButton("Simulation (CoppeliaSim)")
        self.radio_sim.setChecked(True)
        self.radio_real = QRadioButton("Real Robot")
        mode_layout.addWidget(self.radio_sim)
        mode_layout.addWidget(self.radio_real)
        mode_group.setLayout(mode_layout)
        left_panel.addWidget(mode_group)

        conn_layout = QHBoxLayout()
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_robot)
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.disconnect_robot)
        self.btn_disconnect.setEnabled(False)
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)
        left_panel.addLayout(conn_layout)

        control_group = QGroupBox("Motor Control")
        control_layout = QVBoxLayout()
        self.combo_motors = QComboBox()
        self.combo_motors.addItem("All Motors (Sequentially)")
        
        self.btn_run = QPushButton("Test Motor")
        self.btn_run.clicked.connect(self.run_motor_test)
        self.btn_run.setEnabled(False)
        control_layout.addWidget(QLabel("Select Motor:"))
        control_layout.addWidget(self.combo_motors)
        control_layout.addWidget(self.btn_run)
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)

        log_group = QGroupBox("System Logs")
        log_layout = QVBoxLayout()
        self.log_screen = QTextEdit()
        self.log_screen.setReadOnly(True)
        log_layout.addWidget(self.log_screen)
        log_group.setLayout(log_layout)
        left_panel.addWidget(log_group)


        # Right panel for virtual emotion face
        right_panel = QVBoxLayout()
        
        face_group = QGroupBox("Virtual Emotion Face")
        face_layout = QVBoxLayout()
        
        self.virtual_face = VirtualFace()
        face_layout.addWidget(self.virtual_face)
        
        btn_layout = QHBoxLayout()
        for emotion in ["neutral", "happy", "angry", "sad"]:
            btn = QPushButton(emotion.capitalize())
            # Python'un closure mantığı için lambda içinde e=emotion kullanıyoruz
            btn.clicked.connect(lambda checked, e=emotion: self.set_robot_emotion(e))
            btn_layout.addWidget(btn)

        face_layout.addLayout(btn_layout)
        face_group.setLayout(face_layout)
        
        right_panel.addWidget(face_group)
        right_panel.addStretch(1) 

        main_layout.addLayout(left_panel, stretch=2)
        main_layout.addLayout(right_panel, stretch=1)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.log_message("System initialized. Waiting for connection...")

    def log_message(self, message):
        time_str = time.strftime("%H:%M:%S")
        self.log_screen.append(f"[{time_str}] {message}")
        self.log_screen.verticalScrollBar().setValue(
            self.log_screen.verticalScrollBar().maximum()
        )

    def set_robot_emotion(self, emotion_type):
        self.log_message(f"Emotion changed to: {emotion_type.upper()}")
        self.virtual_face.change_emotion(emotion_type)
        # TODO: Will add HTTP request to real robot to change LED colors based on emotion

    def connect_robot(self):
        self.log_message("Connecting... Please wait.")
        QApplication.processEvents()
        
        is_sim = self.radio_sim.isChecked()
        success = self.controller.connect(is_simulation=is_sim)
        
        if success:
            self.log_message("SUCCESS: Connected to the robot.")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.btn_run.setEnabled(True)
            self.update_motor_combobox()

    def disconnect_robot(self):
        self.controller.disconnect()
        self.log_message("Disconnected.")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_run.setEnabled(False)
        self.combo_motors.clear()
        self.combo_motors.addItem("All Motors (Sequentially)")

    def update_motor_combobox(self):
        self.combo_motors.clear()
        self.combo_motors.addItem("All Motors (Sequentially)")
        motor_names = self.controller.get_motor_names()
        for name in motor_names:
            self.combo_motors.addItem(name)
        self.log_message(f"{len(motor_names)} motor(s) loaded.")

    def run_motor_test(self):
        selection = self.combo_motors.currentText()
        
        if selection == "All Motors (Sequentially)":
            self.log_message("Sequential test starting...")
            for motor in self.controller.get_all_motors():
                self.log_message(f"Testing {motor.name}...")
                self.controller.test_single_motor_smoothly(motor, QApplication.processEvents)
                time.sleep(1)
            self.log_message("Sequential test completed.")
        else:
            self.log_message(f"Testing {selection}...")
            motor = self.controller.get_motor_by_name(selection)
            self.controller.test_single_motor_smoothly(motor, QApplication.processEvents)
            self.log_message(f"{selection} test completed.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoppyTesterApp()
    window.show()
    sys.exit(app.exec_())
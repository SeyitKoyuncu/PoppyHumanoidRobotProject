import sys
import os
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QRadioButton, QComboBox, 
                             QTextEdit, QLabel, QGroupBox, QDoubleSpinBox) # QDoubleSpinBox EKLENDI
                             
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
        self.resize(750, 650)

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
        # Connect btn
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_robot)
        
        # Disconnect btn
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.clicked.connect(self.disconnect_robot)
        self.btn_disconnect.setEnabled(False)
        
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)
        left_panel.addLayout(conn_layout)

        # Motor Control Group
        control_group = QGroupBox("Motor Control")
        control_layout = QVBoxLayout()
        
        # Combobox
        self.combo_motors = QComboBox()
        self.combo_motors.addItem("All Motors (Sequentially)")
        control_layout.addWidget(QLabel("Select Motor:"))
        control_layout.addWidget(self.combo_motors)
        
        # Motor Test Button
        self.btn_run = QPushButton("Test Motor")
        self.btn_run.clicked.connect(self.run_motor_test)
        self.btn_run.setEnabled(False)
        control_layout.addWidget(self.btn_run)

        custom_angle_layout = QHBoxLayout()
        custom_angle_layout.addWidget(QLabel("Target Angle:"))
        
        self.spin_angle = QDoubleSpinBox()
        self.spin_angle.setRange(-180.0, 180.0) # Motor açı sınırları
        self.spin_angle.setValue(0.0)
        
        self.btn_goto = QPushButton("Go To Angle")
        self.btn_goto.clicked.connect(lambda: self.controller.goto_custom_angle(
            logFunction=self.log_message,
            motor=self.controller.get_motor_by_name(self.combo_motors.currentText()),
            target_angle=self.spin_angle.value()
        ))
        self.btn_goto.setEnabled(False)
        
        custom_angle_layout.addWidget(self.spin_angle)
        custom_angle_layout.addWidget(self.btn_goto)
        
        control_layout.addLayout(custom_angle_layout)
        
        # Added Line For Visual Separation
        line = QWidget()
        line.setFixedHeight(1)
        line.setStyleSheet("background-color: #c0c0c0;")
        control_layout.addWidget(line)

        # Rady Position Buttons
        control_layout.addWidget(QLabel("Preset Poses:"))
        
        self.btn_rest = QPushButton("Set Rest (Lying) Position")
        self.btn_rest.clicked.connect(self.set_rest_position)
        self.btn_rest.setEnabled(False) 

        self.btn_stand = QPushButton("Stand Up")
        self.btn_stand.clicked.connect(self.stand_up)
        self.btn_stand.setEnabled(False) 

        control_layout.addWidget(self.btn_rest)
        control_layout.addWidget(self.btn_stand)
        
        control_group.setLayout(control_layout)
        left_panel.addWidget(control_group)
        # -----------------------------------------------------

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
            self.btn_goto.setEnabled(True)
            self.btn_stand.setEnabled(True)
            self.btn_rest.setEnabled(True)
            self.update_motor_combobox()

    def disconnect_robot(self):
        self.controller.disconnect()
        self.log_message("Disconnected.")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_run.setEnabled(False)
        self.btn_goto.setEnabled(False)
        self.btn_stand.setEnabled(False)
        self.btn_rest.setEnabled(False)
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

    def set_rest_position(self):
        self.log_message("Setting robot to flat resting position...")
        try:
            for motor in self.controller.get_all_motors():
                motor.goal_position = 0 
                
            self.log_message("Robot is now lying flat.")
        except Exception as e:
            self.log_message(f"Error setting rest position: {str(e)}")

    def stand_up(self):
        # STEP 1: Slight Crunch
        target_step_1 = {
            # Legs are fixed at 0.0 (Acting as an anchor)
            'l_hip_y': 0.0, 
            'r_hip_y': 0.0,
            
            # Lift the waist and chest slightly
            'abs_y': 15.0,  
            'bust_y': 5.0
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_1, 
            duration=1.0, # Short and controlled duration
            movement_name="Step 1: Slight Crunch", 
            waitSituation=True
        )

        time.sleep(1)  # Wait for the robot to ensure it stabilizes


        # STEP 2: Bend Elbows
        target_step_2 = {
            # Legs are still fixed at 0.0
            'l_hip_y': 0.0, 
            'r_hip_y': 0.0,
            
            # MAINTAIN the slightly lifted angle of the torso (Otherwise it falls back)
            'abs_y': 15.0,  
            'bust_y': 5.0,
            
            # Bend elbows 90 degrees (It might need to be -90.0 depending on the motor direction)
            'l_elbow_y': 90.0, 
            'r_elbow_y': 90.0
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_2, 
            duration=1.0, 
            movement_name="Step 2: Bend Elbows", 
            waitSituation=True
        )

        time.sleep(1)
        # Second Step: Move hip motors to lift the torso
        
        # STEP 3: Full Sit-up and Opening Arms
        target_step_3 = {
            # Legs continue to stay fixed at 0.0
            'l_hip_y': 0.0, 
            'r_hip_y': 0.0,
            
            # Reach the target (maximum) angle for waist and chest
            'abs_y': 35.0,  
            'bust_y': 35.0,
            
            # Extend the elbows (0.0) to throw the arms forward
            'l_elbow_y': 0.0,
            'r_elbow_y': 0.0,
            
            # (Optional) Extending shoulders forward provides extra momentum
            'l_shoulder_y': -90.0, 
            'r_shoulder_y': -90.0
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_3, 
            duration=1.2, # A slightly faster duration to generate kinetic energy
            movement_name="Step 3: Full Sit-up", 
            waitSituation=True
        )

        # STEP 4: Transferring the Load to Hips and Full Sit
        target_step_4 = {
            # Since the torso is off the ground, we can now bend the hips. 
            # This folds the torso over the legs, pulling the center of gravity forward.
            'l_hip_y': -45.0,
            'r_hip_y': -45.0,
            
            # We ease the extreme contraction in the waist and chest since the hips are starting to bend.
            # Otherwise, the robot folds in on itself too much.
            'abs_y': 35.0,  
            'bust_y': 35.0,
            
            # Bending the knees slightly prevents the legs from lifting into the air like a long stick 
            # and ensures the heels press against the ground (anchoring).
            'l_knee_y': 5.0,
            'r_knee_y': 5.0,
            
            # Let the arms' momentum continue to balance the torso by pressing slightly down/forward
            'l_shoulder_y': -90.0, 
            'r_shoulder_y': -90.0,
            
            # Elbows can remain straight
            'l_elbow_y': 0.0,
            'r_elbow_y': 0.0
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_4, 
            duration=1.5, # A slightly longer duration for a balanced transition
            movement_name="Step 4: Transition to Hips", 
            waitSituation=True
        )

        # STEP 5: Transferring the Load to Hips and Full Sit
        target_step_5 = {
            # Since the torso is off the ground, we can now bend the hips. 
            # This folds the torso over the legs, pulling the center of gravity forward.
            'l_hip_y': 0.0, 
            'r_hip_y': 0.0,
            
            # We ease the extreme contraction in the waist and chest since the hips are starting to bend.
            # Otherwise, the robot folds in on itself too much.
            'abs_y': 35.0,  
            'bust_y': 35.0,
            
            # Bending the knees slightly prevents the legs from lifting into the air like a long stick 
            # and ensures the heels press against the ground (anchoring).
            'l_knee_y': 5.0,
            'r_knee_y': 5.0,
            
            # Let the arms' momentum continue to balance the torso by pressing slightly down/forward
            'l_shoulder_y': -90.0, 
            'r_shoulder_y': -90.0,
            
            # Elbows can remain straight
            'l_elbow_y': 0.0,
            'r_elbow_y': 0.0
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_5, 
            duration=1.5, # A slightly longer duration for a balanced transition
            movement_name="Step 5: Transition to Hips", 
            waitSituation=True
        )
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoppyTesterApp()
    window.show()
    sys.exit(app.exec_())
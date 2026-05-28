import math
import sys
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QRadioButton, QComboBox, 
                             QTextEdit, QLabel, QGroupBox)
from PyQt5.QtCore import Qt

# Need pypot for controling the Poppy Humanoid robot
try:
    from pypot.creatures import PoppyHumanoid
except ImportError:
    PoppyHumanoid = None
    print("Error: 'pypot' library not found. Please install it.")

class PoppyTesterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.robot = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Poppy Humanoid Test Tool")
        self.resize(500, 600)

        # Main Widget and Layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # 1. Connection mood selection
        mode_group = QGroupBox("Connection Mode")
        mode_layout = QHBoxLayout()
        self.radio_sim = QRadioButton("Simulation (CoppeliaSim)")
        self.radio_sim.setChecked(True)
        self.radio_real = QRadioButton("Real Robot")
        
        mode_layout.addWidget(self.radio_sim)
        mode_layout.addWidget(self.radio_real)
        mode_group.setLayout(mode_layout)
        main_layout.addWidget(mode_group)

        # Connect / Disconnect Buttons
        conn_layout = QHBoxLayout()
        self.btn_connect = QPushButton("Connect to Robot")
        self.btn_connect.clicked.connect(self.connect_robot)
        self.btn_disconnect = QPushButton("Disconnect from Robot")
        self.btn_disconnect.clicked.connect(self.disconnect_robot)
        self.btn_disconnect.setEnabled(False)
        
        conn_layout.addWidget(self.btn_connect)
        conn_layout.addWidget(self.btn_disconnect)
        main_layout.addLayout(conn_layout)

        # 2. Motor Control Section
        control_group = QGroupBox("Motor Control")
        control_layout = QVBoxLayout()
        
        self.combo_motors = QComboBox()
        self.combo_motors.addItem("All Motors (Sequentially)")
        
        self.btn_run = QPushButton("Test Selected Motor")
        self.btn_run.clicked.connect(self.run_motor_test)
        self.btn_run.setEnabled(False)

        control_layout.addWidget(QLabel("Test Motor:"))
        control_layout.addWidget(self.combo_motors)
        control_layout.addWidget(self.btn_run)
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # 3. Log and Error Display
        log_group = QGroupBox("System Logs and Errors")
        log_layout = QVBoxLayout()
        self.log_screen = QTextEdit()
        self.log_screen.setReadOnly(True)
        log_layout.addWidget(self.log_screen)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.log_message("System initialized. Waiting for connection...")

    def log_message(self, message):
        """Prints message and timestamp to the screen."""
        time_str = time.strftime("%H:%M:%S")
        self.log_screen.append(f"[{time_str}] {message}")
        # Scroll to the bottom
        self.log_screen.verticalScrollBar().setValue(
            self.log_screen.verticalScrollBar().maximum()
        )

    def connect_robot(self):
        if PoppyHumanoid is None:
            self.log_message("ERROR: 'pypot' library not found. Connection failed.")
            return

        try:
            self.log_message("Connecting to robot, please wait...")
            QApplication.processEvents() # Prevent interface from freezing during connection

            if self.radio_sim.isChecked():
                self.log_message("CoppeliaSim simulation connection in progress...")
                self.robot = PoppyHumanoid(simulator='vrep')
            else:
                self.log_message("Real robot connection in progress... (Ensure 12V power supply is active and cables are connected.)")
                self.robot = PoppyHumanoid()

            self.log_message("SUCCESS: Connected to the robot.")
            self.btn_connect.setEnabled(False)
            self.btn_disconnect.setEnabled(True)
            self.btn_run.setEnabled(True)
            
            # Add motors to the combobox
            self.update_motor_list()

        except Exception as e:
            self.log_message(f"ERROR: Connection failed. Details: {str(e)}")
            if self.radio_sim.isChecked():
                self.log_message("Hint: Ensure CoppeliaSim is open and the simulation is running.")

    def disconnect_robot(self):
        if self.robot:
            try:
                self.robot.close()
                self.robot = None
                self.log_message("Connection disconnected.")
                self.btn_connect.setEnabled(True)
                self.btn_disconnect.setEnabled(False)
                self.btn_run.setEnabled(False)
                
                # Clear combobox 
                self.combo_motors.clear()
                self.combo_motors.addItem("All Motors (Sequentially)")
            except Exception as e:
                self.log_message(f"ERROR: Error occurred while disconnecting: {str(e)}")

    def update_motor_list(self):
        self.combo_motors.clear()
        self.combo_motors.addItem("All Motors (Sequentially)")
        if self.robot:
            for motor in self.robot.motors:
                self.combo_motors.addItem(motor.name)
        self.log_message(f"{len(self.robot.motors)} motor successfully loaded.")

    def run_motor_test(self):
        if not self.robot:
            self.log_message("ERROR: Robot connection not established.")
            return

        selection = self.combo_motors.currentText()

        try:
            if selection == "All Motors (Sequentially)":
                self.log_message("All motors are being tested sequentially. (Movement: +40 degrees)")
                for motor in self.robot.motors:
                    self.test_single_motor(motor)
                    QApplication.processEvents() # Prevent interface from freezing
                    time.sleep(2) # Short pause between motors
                self.log_message("Sequential test completed.")
            else:
                motor = getattr(self.robot, selection)
                self.log_message(f"{selection} motor is being tested...")
                self.test_single_motor(motor)
                self.log_message(f"{selection} test completed.")
                
        except Exception as e:
            self.log_message(f"ERROR: An error occurred while testing the motor: {str(e)}")

    def test_single_motor(self, motor):
            """Move Motors Smoothly to +40 degrees and back to the original position with cosinus trajectory"""
            current_pos = motor.present_position
            motor.compliant = False 
            
            amplitude = 40.0
            duration = 2.5  # Second for the movements
            dt = 0.05       # 20 hz frequency for smooth updates
            
            # 1. Smooth forward motion
            t = 0.0
            while t <= duration:
                # Normalize time to [0, 1] interval
                normalized_time = t / duration
                
                # Smoot cosinus trajectory calculation (ease-in-out) between 0 and 1s
                smooth_factor = (1.0 - math.cos(math.pi * normalized_time)) / 2.0
                
                # Calculate target position based on the smooth factor
                target = current_pos + (amplitude * smooth_factor)
                
                # Move forward without waiting for completion to allow smooth updates
                motor.goto_position(target, dt, wait=False)
                time.sleep(dt)
                t += dt
                QApplication.processEvents() # Arayüzün donmasını engelle
                
            time.sleep(1) 
            
            # 2. Back to the start point smoothly
            t = 0.0
            while t <= duration:
                normalized_time = t / duration
                smooth_factor = (1.0 - math.cos(math.pi * normalized_time)) / 2.0
                
                # calculate target position for returning to the original position
                target = (current_pos + amplitude) - (amplitude * smooth_factor)
                
                motor.goto_position(target, dt, wait=False)
                time.sleep(dt)
                t += dt
                QApplication.processEvents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoppyTesterApp()
    window.show()
    sys.exit(app.exec_())
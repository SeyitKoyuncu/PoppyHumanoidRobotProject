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

        self.btn_sit = QPushButton("Sit Down")
        self.btn_sit.clicked.connect(self.sit_down)


        self.btn_rest = QPushButton("Set Rest (Lying) Position")
        self.btn_rest.clicked.connect(self.set_rest_position)
        self.btn_rest.setEnabled(False) 

        self.btn_flat = QPushButton("Lay Flat (Reset) Position")
        self.btn_flat.clicked.connect(self.lay_flat_position)
        self.btn_flat.setEnabled(False) 

        control_layout.addWidget(self.btn_rest)
        control_layout.addWidget(self.btn_sit)
        control_layout.addWidget(self.btn_flat)
        
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
            self.btn_sit.setEnabled(True)
            self.btn_rest.setEnabled(True)
            self.btn_flat.setEnabled(True)
            self.update_motor_combobox()

    def disconnect_robot(self):
        self.controller.disconnect()
        self.log_message("Disconnected.")
        self.btn_connect.setEnabled(True)
        self.btn_disconnect.setEnabled(False)
        self.btn_run.setEnabled(False)
        self.btn_goto.setEnabled(False)
        self.btn_sit.setEnabled(False)
        self.btn_rest.setEnabled(False)
        self.btn_flat.setEnabled(False)
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

    def sit_down(self):

        # STEP 6 (FIXED): The Final Stand-up Motion (From deep squat to straight)
        """target_step_1 = {
            # The standing pose
            'l_hip_y': 0.0, 'r_hip_y': 0.0,
            # CRITICAL: Keep X and Z zero during lift
            'l_hip_x': 0.0, 'r_hip_x': 0.0,
            'l_hip_z': 0.0, 'r_hip_z': 0.0,
            # Also zero out other joints for full straight stand
            'l_knee_y': 0.0, 'r_knee_y': 0.0,
            'abs_y': 0.0, 'bust_y': 0.0,
            'l_shoulder_y': 0.0, 'r_shoulder_y': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_1, 
            duration=1.2, # SÜRE UZATILDI (0.5 -> 1.2s): Daha kontrollü, daha az momentum.
            movement_name="Step 6: Final Stand Up", waitSituation=True
        )
       # STEP 7: Bacakları Karna Doğru Bükme (İstikrarlı V-sit)
        target_step_2 = {
            'l_hip_y': -90.0, 'r_hip_y': -90.0,
            'l_knee_y': 120.0, 'r_knee_y': 120.0,
            'abs_y': 30.0,  'bust_y': 30.0,
            
            # --- KRİTİK: Kolları önde tutarak ağırlığı öne çek ---
            'l_shoulder_y': -90.0, 
            'r_shoulder_y': -90.0,
            'l_elbow_y': 0.0, 
            'r_elbow_y': 0.0,
            
            # Simetri korunsun
            'l_hip_x': 0.0, 'r_hip_x': 0.0,
            'l_hip_z': 0.0, 'r_hip_z': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_2, 
            duration=1.5, movement_name="Step 7: Pull Legs (Maintain Front Arms)", waitSituation=True
        )
        time.sleep(1) # Bu pozisyonda dengede durması için bekle


        # STEP 8A (REVISED): Gövdeyi Kapat, Kolları Önde Tut (İvmeyi Yönet)
        target_step_3a = {
            # Bacaklar aynı kalıyor
            'l_hip_y': -90.0, 'r_hip_y': -90.0,
            'l_knee_y': 120.0, 'r_knee_y': 120.0,
            
            # Gövdeyi tam kapasite öne katla (Ama kafayı gömme)
            'abs_y': 45.0,  
            'bust_y': 45.0,
            
            # --- KRİTİK: Kolları hâlâ önde tutarak denge sağla ---
            'l_shoulder_y': -90.0, 
            'r_shoulder_y': -90.0,
            'l_elbow_y': 0.0, 
            'r_elbow_y': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_3a, 
            duration=1.8, # Geriye ivmeyi önlemek için yumuşak, uzun geçiş (1.8 saniye)
            movement_name="Step 8A: Fold Torso (Arms Stabilize)", 
            waitSituation=True
        )
        time.sleep(1) # Stabilize olmasını bekle


        # STEP 8B (FIXED): Kafayı Göm ve Kolları Dizlere Sar (Ağırlığı Önde Tut)
        target_step_3b = {
            # Bacaklar ve Gövde aynı kalıyor
            'l_hip_y': -90.0, 'r_hip_y': -90.0,
            'l_knee_y': 120.0, 'r_knee_y': 120.0,
            'abs_y': 45.0,  'bust_y': 45.0,
            
            # Kafayı gömüyoruz
            'head_y': 40.0, 
            
            # --- KRİTİK DÜZELTME: KOLLAR ---
            # Omuzları çok geriye çekmek yerine dizlere doğru (-60.0) açılı bırakıyoruz.
            # Böylece kolların ağırlığı gövdenin önünde kalıp geriye düşüşü engeller.
            'l_shoulder_y': -60.0, 
            'r_shoulder_y': -60.0,
            
            # Dirsekleri bükerek bacaklara sarılma efekti veriyoruz
            'l_elbow_y': 60.0, 
            'r_elbow_y': 60.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_3b, 
            duration=2.0, # ÇOK ÖNEMLİ: Hareketi 2.0 saniyeye yayarak sarsıntıyı ve ivmeyi sıfırlıyoruz
            movement_name="Step 8B: Tuck Head and Wrap Arms", 
            waitSituation=True
        )"""
        target_step_4 = {
            'l_hip_y': -90.0, 
            'r_hip_y': -90.0,
            
            'l_knee_y': 0.0, 
            'r_knee_y': 0.0,
            'l_ankle_y': 0.0,
            'r_ankle_y': 0.0,
            'l_hip_x': 0.0, 'r_hip_x': 0.0,
            'l_hip_z': 0.0, 'r_hip_z': 0.0,
            
            # Gövdeyi tamamen dikleştir (abs ve bust 0.0)
            'abs_y': 0.0,  
            'bust_y': 0.0,
            
            # Kafayı kaldır ve ileriye bak
            'head_y': 0.0, 
            
            # Kolları iki yana serbest bırak (Omuzlar ve dirsekler düz)
            'l_shoulder_y': 0.0, 
            'r_shoulder_y': 0.0,
            'l_elbow_y': 0.0, 
            'r_elbow_y': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_4, 
            duration=2.5, # ÇOK ÖNEMLİ: Bu açılma hareketinin süresi uzun (2.5 sn) olmalı ki momentum robotu savurmasın.
            movement_name="Step 9: Open to L-Sit Position", 
            waitSituation=True
        )
       # STEP 5A: Sadece Gövdeyi Maksimuma Katla (Kalçayı Henüz Bükme!)
        target_step_5A = {
            # Kalçalar 0.0'da (Bacaklar dümdüz ve yerde ağır bir çapa gibi kalıyor)
            'l_hip_y': 0.0, 
            'r_hip_y': 0.0,
            'l_knee_y': 0.0, 'r_knee_y': 0.0,
            
            # SADECE gövde motorlarını limitlerine kadar öne basıyoruz
            'abs_y': 70.0,  
            'bust_y': 70.0,
            'head_y': 40.0, # Kafayı da iyice öne göm ki ağırlık öne kaysın
            
            # Kolları ileri fırlat
            'l_shoulder_y': -90.0, 'r_shoulder_y': -90.0,
            
            'l_hip_x': 0.0, 'r_hip_x': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_5A, 
            duration=1.0, 
            movement_name="Step 5A: Max Torso Crunch (Legs Flat)", 
            waitSituation=True
        )


        # STEP 5B: Ağırlık Öndeyken Kalçayı Bükerek Oturma Pozisyonuna Geç
        target_step_5B = {
            # Gövde 70 derecede öne katlı kalmaya devam ediyor (Geriye düşmemek için)
            'abs_y': 70.0,  
            'bust_y': 70.0,
            'head_y': 40.0,
            'l_shoulder_y': -90.0, 'r_shoulder_y': -90.0,
            
            # ŞİMDİ kalçayı -90'a çekiyoruz. Gövde zaten önde olduğu için geriye düşemez.
            'l_hip_y': -90.0, 
            'r_hip_y': -90.0,
            
            'l_knee_y': 0.0, 'r_knee_y': 0.0,
            'l_hip_x': 0.0, 'r_hip_x': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_5B, 
            duration=1.0, 
            movement_name="Step 5B: Engage Hips to Sit", 
            waitSituation=True
        )

        # STEP 5B: Ağırlık Öndeyken Kalçayı Bükerek Oturma Pozisyonuna Geç
        target_step_5B = {
            # Gövde 70 derecede öne katlı kalmaya devam ediyor (Geriye düşmemek için)
            'abs_y': 70.0,  
            'bust_y': 70.0,
            'head_y': 40.0,
            'l_shoulder_y': -90.0, 'r_shoulder_y': -90.0,
            
            # ŞİMDİ kalçayı -90'a çekiyoruz. Gövde zaten önde olduğu için geriye düşemez.
            'l_hip_y': -90.0, 
            'r_hip_y': -90.0,
            
            'l_knee_y': 0.0, 'r_knee_y': 0.0,
            'l_hip_x': 0.0, 'r_hip_x': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_step_5B, 
            duration=1.0, 
            movement_name="Step 5B: Engage Hips to Sit", 
            waitSituation=True
        )

    
    def lay_flat_position(self):
        self.log_message("Robot sırtüstü devriliyor (Trust Fall)...")
        
        # Adım 1: Bacakları Öne Fırlat
        # Gövdeyi bükmeye çalışmıyoruz. Sadece kalçadan bacakları öne (havaya) kaldırıyoruz.
        # Ayakların altındaki zemin desteği kaybolunca robot mecburen sırtüstü düşecek.
        target_fall_backward = {
            # Kalçayı 60 derece bükerek bacakları havaya (öne) tekmeliyoruz
            'l_knee_y': 20.0, 
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_fall_backward, 
            duration=0.5, # Çok hızlı olmalı ki bacaklar anında yerden kesilsin
            movement_name="Step 1: Kick Legs Forward & Fall", 
            waitSituation=True
        )

        time.sleep(2) 

        target_flat = {
            'l_hip_y': 0.0, 'r_hip_y': 0.0,
            'l_knee_y': 0.0, 'r_knee_y': 0.0,
            'l_ankle_y': 0.0, 'r_ankle_y': 0.0,
            'abs_y': 0.0, 'bust_y': 0.0,
            'head_y': 0.0,
            'l_shoulder_y': 0.0, 'r_shoulder_y': 0.0,
            'l_elbow_y': 0.0, 'r_elbow_y': 0.0,
        }
        
        self.controller.motor_movement_go_to(
            logFunction=self.log_message, 
            target_angles=target_flat, 
            duration=1.5, # Robot yerde sekerken yavaşça düzeltiyoruz
            movement_name="Step 2: Lay Flat on Ground", 
            waitSituation=True
        )

       
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PoppyTesterApp()
    window.show()
    sys.exit(app.exec_())
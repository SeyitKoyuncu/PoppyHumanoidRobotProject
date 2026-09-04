import serial
import serial.tools.list_ports
import threading
import time

class IMUController:
    """Thread-based background reader for SparkFun 9DoF IMU."""
    
    def __init__(self, target_vid=0x1B4F, baudrate=115200):
        self.target_vid = target_vid
        self.baudrate = baudrate
        self.serial_conn = None
        
        self.latest_yaw = 0.0
        self.latest_pitch = 0.0
        self.latest_roll = 0.0
        
        self.pitch_offset = 0.0  # Standing posture reference angle
        self.is_running = False
        self.thread = None

    def connect(self):
        """Dynamically finds and opens the IMU port using the VID 0x1B4F filter."""
        imu_port = None
        for dev in serial.tools.list_ports.comports():
            if dev.vid == self.target_vid or dev.vid == 6991:
                imu_port = dev.device
                break

        if not imu_port:
            print("[IMU ERROR] SparkFun IMU not found!")
            return False

        try:
            self.serial_conn = serial.Serial(imu_port, self.baudrate, timeout=0.1)
            time.sleep(1.5)  # Wait for the board's startup reset
            
            self.is_running = True
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()
            print(f"[IMU INFO] Data stream started on {imu_port}.")
            return True
        except Exception as e:
            print(f"[IMU ERROR] Connection error: {e}")
            return False

    def _update_loop(self):
        """Reads and parses the latest line from the serial port."""
        while self.is_running and self.serial_conn and self.serial_conn.is_open:
            try:
                line = self.serial_conn.readline().decode('utf-8', errors='ignore').strip()
                if line.startswith("#YPR="):
                    parts = line.replace("#YPR=", "").split(",")
                    if len(parts) == 3:
                        self.latest_yaw = float(parts[0])
                        self.latest_pitch = float(parts[1])
                        self.latest_roll = float(parts[2])
            except Exception:
                pass
            time.sleep(0.005)

    def calibrate_standing_reference(self, sample_duration=1.0):
        """Calibrates zero reference angle while the robot is standing upright."""
        print("[IMU] Calculating standing reference angle, keep the robot steady...")
        samples = []
        start_time = time.time()
        while time.time() - start_time < sample_duration:
            samples.append(self.latest_pitch)
            time.sleep(0.02)
            
        if samples:
            self.pitch_offset = sum(samples) / len(samples)
            print(f"[IMU] Reference pitch angle saved: {self.pitch_offset:.2f}°")

    def get_pitch_error(self):
        """Returns the deviation from the reference standing posture (Error Angle)."""
        return self.latest_pitch - self.pitch_offset

    def disconnect(self):
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        print("[IMU] Connection closed.")
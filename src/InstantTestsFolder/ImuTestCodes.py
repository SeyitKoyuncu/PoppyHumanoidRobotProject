import serial
import serial.tools.list_ports
import time


# Find IMU dynamically
imu_port = None
for dev in serial.tools.list_ports.comports():
    if dev.vid == 0x1B4F or dev.vid == 6991:
        imu_port = dev.device
        break

if not imu_port:
    print("Cant find the IMU please control it.")
    exit()

print(f"IMU finded {imu_port}")

# 2. Open the serial port and listen the IMU data
try:
    ser = serial.Serial(imu_port, 115200, timeout=1)
    time.sleep(2)  # Wait for the IMU to initialize
    
    print("Sensor Data starting for quit pls CTRL + C:\n")
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print("IMU Output:", line)
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nProcess interrupted by user.")
except Exception as e:
    print(f"Hata: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
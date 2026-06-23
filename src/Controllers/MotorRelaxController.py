import pypot.dynamixel
import serial.tools.list_ports
import os


def force_relax_motors():
    print("\n" + "=" * 50)
    print("ROBOT RELAXATION PROTOCOL INITIATING...")
    print("=" * 50)

    # 1. Detect motor ports (using VID: 5840 / 0x16D0 filter)
    all_devices = serial.tools.list_ports.comports()
    motor_ports = [device.device for device in all_devices if device.vid == 5840]

    if not motor_ports:
        print("[ERROR] No active motor port (VID: 5840) found in the system!")
        print("Please ensure the power is on and the USB cables are connected.")
        exit()

    print(f"Detected {len(motor_ports)} motor lines in the system: {motor_ports}\n")

    # 2. Iterate through each port and disable torques (relax muscles)
    for port in motor_ports:
        # Precaution against locked ports
        os.system(f'sudo fuser -k {port} > /dev/null 2>&1')
        
        try:
            with pypot.dynamixel.DxlIO(port, use_sync_read=False) as dxl_io:
                ids = dxl_io.scan(range(254))
                
                if ids:
                    # disable_torque() completely turns off the motor's muscle power (same as compliant = True)
                    dxl_io.disable_torque(ids)
                    print(f"[APPROVED] {len(ids)} motors on [{port}] have been completely released. (IDs: {ids})")
                else:
                    print(f"[WARNING] No motors found on [{port}].")
                    
        except Exception as e:
            print(f"[ERROR] Failed to access port [{port}]: {e}")

    print("\n[COMPLETED] Process completed! The robot's motors are now completely free; you can carry it safely.")   

def relax_motors(poppy):
    if poppy is not None:
        for m in poppy.motors:
            m.compliant = True
        poppy.close()
        print("Serial port released. Safe to run another script.")
        
if __name__ == "__main__":
    force_relax_motors()
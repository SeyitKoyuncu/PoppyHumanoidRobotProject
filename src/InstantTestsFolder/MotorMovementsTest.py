import os
import json
import time
import math
import pypot.dynamixel
import poppy_humanoid

def test_working_motors_low_level(found_ids):
    """Bypasses PoppyHumanoid class and controls motors directly via DxlIO."""
    
    print("\n" + "=" * 56)
    print("HARDWARE TEST STARTING (LOW-LEVEL DxlIO BYPASS)...")
    print("=" * 56)
    
    # 1. Find available ports
    ports = pypot.dynamixel.get_available_ports()
    if not ports:
        print("[ERROR] No USB port found. Please unplug and replug the cable.")
        return
        
    port = ports[0] # Take the first found port (Usually /dev/ttyACM0)
    print(f"Connected Port: {port}")
    
    dxl_io = None
    try:
        # 2. Connect directly to the hardware (Bypassing the PoppyHumanoid class)
        dxl_io = pypot.dynamixel.DxlIO(port)
        print("✅ Direct hardware connection successful!\n")
        
        # 3. Test only the working motors
        for m_id in found_ids:
            # First, verify if the motor is actually reachable on the port
            if not dxl_io.ping(m_id):
                print(f"❌ ID {m_id} is unreachable, skipping...")
                continue
                
            print(f"> Testing Motor ID: {m_id}...")
            
            # Enable torque and get the present position of the motor
            dxl_io.enable_torque([m_id])
            current_pos = dxl_io.get_present_position([m_id])[0]
            
            amplitude = 20.0
            duration = 1.5
            dt = 0.05
            
            # Forward Motion
            t = 0.0
            while t <= duration:
                smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
                target = current_pos + (amplitude * smooth_factor)
                dxl_io.set_goal_position({m_id: target})
                time.sleep(dt)
                t += dt
                
            time.sleep(0.5)
            
            # Backward Motion
            t = 0.0
            while t <= duration:
                smooth_factor = (1.0 - math.cos(math.pi * (t / duration))) / 2.0
                target = (current_pos + amplitude) - (amplitude * smooth_factor)
                dxl_io.set_goal_position({m_id: target})
                time.sleep(dt)
                t += dt
                
        print("\nAll motor tests completed successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] DxlIO communication error: {e}")
        
    finally:
        # Ensure the port is closed and released even if an error occurs
        if dxl_io is not None:
            dxl_io.close()
            print("Port successfully closed and released.")


if __name__ == '__main__':
    # 1. Forcefully clear the old locked port one last time 
    os.system('sudo fuser -k /dev/ttyACM0 > /dev/null 2>&1')
    time.sleep(1)

    # 2. Read the configuration file
    try:
        config_path = os.path.join(os.path.dirname(poppy_humanoid.__file__), 'configuration', 'poppy_humanoid.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        expected_motors = config.get('motors', {})
    except Exception as e:
        print(f"Cannot read configuration file: {e}")
        expected_motors = {}

    # The healthy IDs detected in your previous scan:
    found_ids = [11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35, 36, 37]
    
    if expected_motors:
        print(f"\n{'Motor Name':<22} | {'Expected ID':<12}")
        print("=" * 40)
        
        for name, info in sorted(expected_motors.items(), key=lambda x: x[1].get('id', 0)):
            m_id = info.get('id')
            if m_id in found_ids:
                print(f"{name:<22} | {m_id:<12} | ✅ OK")
            else:
                print(f"{name:<22} | {m_id:<12} | ❌ MISSING")
                
        print("=" * 40)
        
        # Start the low-level hardware test
        test_working_motors_low_level(found_ids)
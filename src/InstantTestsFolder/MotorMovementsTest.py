import os
import json
import time
import math
import pypot.dynamixel
import poppy_humanoid
import serial.tools.list_ports

def test_working_motors_low_level(port_motor_map):
    """
    Bypasses PoppyHumanoid class and controls motors directly via DxlIO.
    Uses the dynamic port_motor_map to know exactly which port to open for which motor.
    """
    print("\n" + "=" * 56)
    print("HARDWARE TEST STARTING (DYNAMIC MULTI-PORT BYPASS)...")
    print("=" * 56)
    
    if not port_motor_map:
        print("[WARNING] No motors to test. Exiting.")
        return

    # Iterate through each port and its associated motor IDs
    for port, m_ids in port_motor_map.items():
        print(f"\n>>> Connecting to {port} to test {len(m_ids)} motors...")
        
        dxl_io = None
        try:
            # Connect to the specific port for this batch of motors
            dxl_io = pypot.dynamixel.DxlIO(port, use_sync_read=False)
            print(f"✅ Connection successful on {port}!\n")
            
            for m_id in m_ids:
                if not dxl_io.ping(m_id):
                    print(f"❌ ID {m_id} is unreachable on {port}, skipping...")
                    continue
                    
                print(f"> Testing Motor ID: {m_id} on {port}...")
                
                # Enable torque and get the present position of the motor
                dxl_io.enable_torque([m_id])
                current_pos = dxl_io.get_present_position([m_id])[0]
                
                amplitude = 20.0
                duration = 1.5
                dt = 0.05
                
                # Forward Motion (Smooth Sine Wave)
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
                    
            print(f"\nAll motor tests on {port} completed successfully.")
            
        except Exception as e:
            print(f"\n[ERROR] DxlIO communication error on {port}: {e}")
            
        finally:
            # Ensure the specific port is closed before moving to the next USB port
            if dxl_io is not None:
                dxl_io.close()
                print(f"🔒 Port {port} successfully closed and released.")

if __name__ == '__main__':
    # 1. Dynamically find all USB ports belonging to the motors (VID: 5840 / 0x16D0)
    print("Detecting valid motor ports (VID: 5840)...")
    all_devices = serial.tools.list_ports.comports()
    motor_ports = [device.device for device in all_devices if device.vid == 5840]

    if not motor_ports:
        print("[ERROR] No valid motor port (VID: 5840) found. Please unplug and replug the cables.")
        exit()

    print(f"Valid ports found: {motor_ports}\n")

    port_motor_map = {}
    total_found_ids = []

    # 2. Force clear and scan each valid port dynamically
    for port in motor_ports:
        # Clear the specific locked port
        os.system(f'sudo fuser -k {port} > /dev/null 2>&1')
        time.sleep(1)

        try:
            with pypot.dynamixel.DxlIO(port, use_sync_read=False) as dxl_io:
                print(f"Scanning hardware on {port} for active motors, please wait...")
                ids = dxl_io.scan(range(254))
                
                if ids:
                    port_motor_map[port] = ids
                    total_found_ids.extend(ids)
                    print(f"  -> Found active IDs on {port}: {ids}\n")
                else:
                    print(f"  -> No motors found on {port}.\n")
                    
        except Exception as e:
            print(f"Hardware scan error on {port}: {e}\n")

    # Sort the total list for a clean comparison
    total_found_ids = sorted(list(set(total_found_ids)))

    # 3. Read the configuration file
    try:
        config_path = os.path.join(os.path.dirname(poppy_humanoid.__file__), 'configuration', 'poppy_humanoid.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        expected_motors = config.get('motors', {})
    except Exception as e:
        print(f"Cannot read configuration file: {e}")
        expected_motors = {}

    # 4. Compare expected vs total found
    if expected_motors and total_found_ids:
        print(f"\n{'Motor Name':<22} | {'Expected ID':<12} | {'Status':<15}")
        print("=" * 56)
        
        missing_count = 0
        for name, info in sorted(expected_motors.items(), key=lambda x: x[1].get('id', 0)):
            m_id = info.get('id')
            if m_id in total_found_ids:
                print(f"{name:<22} | {m_id:<12} | ✅ OK")
            else:
                print(f"{name:<22} | {m_id:<12} | ❌ MISSING")
                missing_count += 1
                
        print("=" * 56)
        print(f"Ready to test {len(total_found_ids)} motors across {len(port_motor_map)} ports. {missing_count} motors are missing.")
        
        # 5. Start the low-level hardware test passing the dynamic map
        #test_working_motors_low_level(port_motor_map)
        
    elif not total_found_ids:
        print("\n[WARNING] No motors were found on the bus. Hardware test aborted.")
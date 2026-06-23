import os
import json
import pypot.dynamixel
import poppy_humanoid
import serial

found_ids = []
try:
    # Find all serial ports
    all_devices = serial.tools.list_ports.comports()
    
    motor_ports = []
    for device in all_devices:
        #print(device.vid)
        if device.vid == 5840: 
            motor_ports.append(device.device)
            
    if not motor_ports:
        print("[ERROR] Cant Find any dynamxiel port!")
    else:
        print(f"Filtered Motor Control Ports: {motor_ports}")
        
        # Just scan filterd ports
        for port in motor_ports:
            print(f"\n>>> [{port}] Scanning, Please Wait...")
            try:
                with pypot.dynamixel.DxlIO(port, use_sync_read=False) as dxl_io:
                    ids_in_port = dxl_io.scan(range(254))
                    print(f"Motors on [{port}]: {ids_in_port}")
                    found_ids.extend(ids_in_port)
            except Exception as port_error:
                print(f"[ERROR] When reading {port}: {port_error}")
        
        found_ids = sorted(list(set(found_ids)))
        print(f"\n All unique Motor IDs: {found_ids}")

except Exception as e:
    print(f"Hardware scan error: {e}")

# 2. Read the Poppy configuration file
try:
    config_path = os.path.join(os.path.dirname(poppy_humanoid.__file__), 'configuration', 'poppy_humanoid.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    expected_motors = config.get('motors', {})
except Exception as e:
    print(f"Can not read configuration file: {e}")
    expected_motors = {}

# 3. Compare the actually found IDs (found_ids) with the expected ones
if expected_motors:
    print(f"\n{'Motor Name':<22} | {'Waited ID':<12} | {'Status':<15}")
    print("=" * 56)
    
    missing_count = 0
    # Check in order of ID
    for name, info in sorted(expected_motors.items(), key=lambda x: x[1].get('id', 0)):
        m_id = info.get('id')
        
        # Now it looks at the list returned from the hardware, not the manually written list
        if m_id in found_ids:
            status = "✅ Connection OK"
        else:
            status = "❌ Can not connected"
            missing_count += 1
            
        print(f"{name:<22} | {m_id:<12} | {status:<15}")
        
    print("=" * 56)
    print(f"Result: {len(found_ids)} motors axis connected. {missing_count} motors axis can not connected!")
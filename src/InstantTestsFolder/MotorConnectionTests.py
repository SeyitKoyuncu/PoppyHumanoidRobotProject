import os
import json
import poppy_humanoid

# Access Poppys official motor list
try:
    config_path = os.path.join(os.path.dirname(poppy_humanoid.__file__), 'configuration', 'poppy_humanoid.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    expected_motors = config.get('motors', {})
except Exception as e:
    print(f"Can not read configuration file: {e}")
    expected_motors = {}

# Founded active motor IDs
found_ids = [11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 31, 32, 33, 34, 35, 36, 37]

if expected_motors:
    print(f"\n{'Motor Name':<22} | {'Waited ID':<12} | {'Status':<15}")
    print("=" * 56)
    
    missing_count = 0
    # Check motors with ID sequence
    for name, info in sorted(expected_motors.items(), key=lambda x: x[1].get('id', 0)):
        m_id = info.get('id')
        if m_id in found_ids:
            status = "✅ Connection OK"
        else:
            status = "❌ Can not connected"
            missing_count += 1
        print(f"{name:<22} | {m_id:<12} | {status:<15}")
        
    print("=" * 56)
    print(f"Result: {len(found_ids)} motors axis connected. {missing_count} motors axis can not connected!")
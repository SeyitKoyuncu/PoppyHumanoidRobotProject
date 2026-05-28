from pypot.creatures import PoppyHumanoid
import time

print("--- Poppy Starting ---")

try:
    poppy = PoppyHumanoid(check_full_config=False)
    
    for m in poppy.motors:
        m.compliant = False
    
    print("Move starting")
    
    poppy.head_z.goal_position = 30
    time.sleep(1.5)
    poppy.head_z.goal_position = -30
    time.sleep(1.5)
    poppy.head_z.goal_position = 0
    
    print("Test successful!")

except Exception as e:
    print(f"Error occur: {e}")

finally:
    # Make motors free
    if 'poppy' in locals():
        for m in poppy.motors:
            m.compliant = True
        print("Motors are now free.")
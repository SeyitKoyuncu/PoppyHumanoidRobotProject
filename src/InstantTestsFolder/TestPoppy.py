import time
from pypot.creatures import PoppyHumanoid

print("--- Welcome to the Poppy Motor Test Tool ---")

try:
    # check_full_config=False prevents the system from crashing even if some motors are missing
    poppy = PoppyHumanoid(check_full_config=False)
    
    print("\n=== Connected Motors ===")
    # Loop through the available motors and print their IDs and names formatted
    for motor in poppy.motors:
        print(f"ID: {motor.id:2d} | Name: {motor.name}")
    print("===========================\n")
    
    # Get input from the user (can be a name or an ID)
    selection = input("Please enter the name or ID of the motor you want to test: ").strip()
    
    # Find the selected motor based on the user input
    selected_motor = None
    for motor in poppy.motors:
        # Match either the string version of the ID or the case-insensitive name
        if str(motor.id) == selection or motor.name.lower() == selection.lower():
            selected_motor = motor
            break
            
    # If a match is found, start the test
    if selected_motor:
        print(f"\n> Testing motor [{selected_motor.name}] (ID: {selected_motor.id})...")
        
        # Make the motor stiff (compliant = False) so it can move
        selected_motor.compliant = False
        
        # Read the current position (We will move relative to this position for safety)
        start_position = selected_motor.present_position
        
        print("Movement 1: Forward (+20 degrees)...")
        selected_motor.goal_position = start_position + 20
        time.sleep(1.5)
        
        print("Movement 2: Backward (-20 degrees)...")
        selected_motor.goal_position = start_position - 20
        time.sleep(1.5)
        
        print("Movement 3: Returning to starting position...")
        selected_motor.goal_position = start_position
        time.sleep(1.5)
        
        print("\nTest completed successfully!")
        
    else:
        print(f"\n ERROR: No motor found with name or ID '{selection}' in the system.")

except Exception as e:
    print(f"\n[ERROR] An unexpected hardware error occurred: {e}")

finally:
    # Cleanup operations: Release motors and clear the port even if the code fails
    if 'poppy' in locals() and poppy is not None:
        for m in poppy.motors:
            m.compliant = True
        
        poppy.close() # Crucial command to prevent port locking
        print("\n Motors have been released and the port has been securely closed.")
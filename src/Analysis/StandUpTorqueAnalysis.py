import time
import sys
import matplotlib.pyplot as plt
import os

from pypot.creatures import PoppyHumanoid

current_dir = os.path.dirname(os.path.abspath(__file__))
scene_path = os.path.join(current_dir, 'Scenes', 'StandUpPositionScene.ttt')


def get_user_confirmation(prompt_message):
    """
    Helper function to ask the user a yes/no question.
    Returns True if the user types 'y' or 'yes', False otherwise.
    """
    while True:
        response = input(f"{prompt_message} (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def main():
    # --- Step 1: Connection Confirmation ---
    if not get_user_confirmation("Do you want to connect to the simulation?"):
        print("Operation cancelled. Exiting program.")
        sys.exit(0) 

    print("Connecting to CoppeliaSim via PyPot...")
    
    try:
        poppy = PoppyHumanoid(simulator='vrep', scene=scene_path)
    except Exception as e:
        print(f"Connection failed. Is CoppeliaSim running? Error: {e}")
        sys.exit(1)

    print("Successfully connected to the simulated robot.")

    # Enable torque and set the motor to hold position
    poppy.abs_y.compliant = False

    # Move to the starting position (lying down)
    print("Moving robot to the initial lying position (0 degrees)...")
    poppy.abs_y.goal_position = 0
    time.sleep(2) # Wait for the robot to stabilize in the simulation

    # --- Step 2: Test Execution Confirmation ---
    print("\nRobot is ready in the lying position.")
    if not get_user_confirmation("Do you want to start the sit-up torque test?"):
        print("Test cancelled by user. Closing connection safely...")
        poppy.close()
        sys.exit(0)

    print("Starting the sit-up motion...")
    
    # Data collection lists
    time_data = []
    torque_data = []

    # Set the target position to 90 degrees (sit-up motion)
    poppy.abs_y.goal_position = 90
    
    start_time = time.time()
    simulation_duration = 5.0  # Duration to record data (in seconds)

    simulation_max_torque = 6.0
    # Data collection loop
    print("Recording torque data...")
    while (time.time() - start_time) < simulation_duration:
        current_time = time.time() - start_time
        
        # Read the current load (This is PERCENTAGE: 0-100)
        raw_load_percentage = abs(poppy.abs_y.present_load)
        
        # Convert percentage to Newton-meters (N.m)
        real_torque_nm = (raw_load_percentage / 100.0) * simulation_max_torque
        
        time_data.append(current_time)
        torque_data.append(real_torque_nm)
        
        # Small delay
        time.sleep(0.05)

    print("Motion completed. Processing data...")

    # Close the PyPot connection safely
    poppy.close()

    # --- Step 3: Plotting ---
    plt.figure(figsize=(10, 6))
    plt.plot(time_data, torque_data, label="Applied Torque (Simulation)", color='blue', linewidth=2)
    
    # MX-28 Stall Torque limit for comparison
    mx28_stall_torque = 2.5 # N.m (from Dynamixel MX-28 datasheet)
    plt.axhline(y=mx28_stall_torque, color='red', linestyle='--', linewidth=2, label="MX-28 Max Torque Limit (2.5 N.m)")
    
    # Graph configurations
    plt.title("Torque Analysis: Lying to Sitting Position (abs_y joint)")
    plt.xlabel("Time (Seconds)")
    plt.ylabel("Torque (N.m)")
    plt.legend()
    plt.grid(True)
    
    # Save and show the plot
    plt.savefig("StandUp_Torque_Result.png")
    print("Graph saved as 'StandUp_Torque_Result.png'. Displaying the graph...")
    plt.show()

if __name__ == '__main__':
    main()
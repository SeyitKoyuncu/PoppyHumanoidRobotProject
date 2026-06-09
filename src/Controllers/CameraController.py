import cv2
import time
import numpy as np

class CameraController:
    """
    Handles camera abstraction. 
    It dynamically switches between the local PC webcam (for local testing/development) 
    and the Poppy Humanoid's internal camera (for real deployment).
    """
    def __init__(self, is_robot=False, robot_instance=None):
        """
        :param is_robot: Boolean flag. Set to False for local development, True for robot deployment.
        :param robot_instance: The pypot robot object (only needed if is_robot=True).
        """
        self.is_robot = is_robot
        self.robot = robot_instance
        self.capture = None # OpenCV VideoCapture object for local webcam

    def set_mode(self, is_robot, robot_instance=None):
        """Allows switching modes on the fly before starting the camera."""
        self.is_robot = is_robot
        self.robot = robot_instance

    def start_camera(self):
        """Initializes the correct video stream based on the environment."""
        if self.is_robot:
            # --- ROBOT CAMERA MODE (pypot) ---
            if self.robot and hasattr(self.robot, 'camera'):
                print("Starting Poppy's internal camera (pypot)...")
                # pypot initializes the camera automatically upon connection, 
                # but we verify its existence here.
                return True
            else:
                print("ERROR: Robot instance has no camera module configured in pypot.")
                return False
        else:
            # --- LOCAL WEBCAM MODE (OpenCV) ---
            print("Starting local PC webcam (OpenCV)...")
            self.capture = cv2.VideoCapture(0)
            
            if not self.capture.isOpened():
                print("ERROR: Could not open local webcam. Check permissions.")
                return False
            return True

    def get_frame(self):
        """
        Reads a single frame from the active video source.
        Returns a tuple: (success_boolean, frame_array_in_BGR_format)
        """
        if self.is_robot:
            # Fetch frame from Poppy's hardware
            if self.robot and hasattr(self.robot, 'camera'):
                try:
                    # Depending on the pypot version, it could be .frame or .read()
                    frame = getattr(self.robot.camera, 'frame', None)
                    if frame is not None and len(frame) > 0:
                        return True, frame
                except Exception as e:
                    print(f"WARNING: Frame drop from robot camera: {str(e)}")
            return False, None
            
        else:
            # Fetch frame from local PC webcam
            if self.capture and self.capture.isOpened():
                ret, frame = self.capture.read()
                if ret:
                    return True, frame
            return False, None

    def stop_camera(self):
        """Releases hardware resources safely."""
        if not self.is_robot:
            if self.capture:
                self.capture.release()
                self.capture = None
                print("Local webcam released.")
        else:
            print("Robot camera feed paused.")
            # Robot controller will handle the camera lifecycle, so we just log this action.

    def run_test(self):
        """
        Runs an isolated test for the camera initialization, frame reading, 
        and hardware release processes. Prints all outputs to the console.
        """
        print("\n" + "="*50)
        print("📷 CAMERA CONTROLLER DIAGNOSTIC TEST 📷")
        print(f"MODE: {'REAL ROBOT (pypot)' if self.is_robot else 'LOCAL PC (OpenCV)'}")
        print("="*50)

        # 1. Start the camera
        success = self.start_camera()
        if not success:
            print("\n>>> TEST ABORTED: Camera initialization failed. <<<")
            return

        time.sleep(1.0) # Hardware warm-up

        # 2. Read a single frame
        ret, frame = self.get_frame()

        if ret and frame is not None:
            print(f">>> SUCCESS: Frame retrieved! Resolution: {frame.shape[1]}x{frame.shape[0]}")
        else:
            print("\n>>> FAILED: Camera initialized but no frame could be read.")

        # 3. Stop the camera
        print("-" * 50)
        self.stop_camera()
        
        print("="*50)
        print("TEST COMPLETED")
        print("="*50 + "\n")


if __name__ == '__main__':
    test_controller = CameraController(is_robot=False)
    test_controller.run_test()
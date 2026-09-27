# Poppy Humanoid Robot Project

A modular control, testing, and simulation framework for the **Poppy Humanoid** robot, executed directly on a **Raspberry Pi 5**. This repository contains low-level hardware controllers, standalone hardware diagnostic tests, an active IMU balance pipeline, voice-action routines, and a simulation-to-real torque analysis workflow.

## Table of Contents
- [Poppy Humanoid Robot Project](#poppy-humanoid-robot-project)
  - [Table of Contents](#table-of-contents)
  - [Hardware \& Tech Stack](#hardware--tech-stack)
  - [Quick Start: How to Run on Raspberry Pi 5](#quick-start-how-to-run-on-raspberry-pi-5)
    - [1. Connection \& Setup](#1-connection--setup)
    - [2. Activate the Virtual Environment](#2-activate-the-virtual-environment)
    - [3. Dependencies \& System Packages](#3-dependencies--system-packages)
      - [System-level TTS Engine (pyttsx3 Requirement)](#system-level-tts-engine-pyttsx3-requirement)
      - [Python Packages](#python-packages)
    - [4. Running the Code](#4-running-the-code)
  - [Emergency Stop \& Reset Procedure](#emergency-stop--reset-procedure)
    - [Step 1: Kill Hanging Processes and Free Serial Ports](#step-1-kill-hanging-processes-and-free-serial-ports)
    - [Step 2: Power Cycle the Motors](#step-2-power-cycle-the-motors)
  - [Project Structure \& Script Overview](#project-structure--script-overview)
    - [Analysis](#analysis)
    - [PoppyTestGUI](#poppytestgui)
    - [InstantTestFolder (Hardware \& Feature Tests)](#instanttestfolder-hardware--feature-tests)
    - [Controllers](#controllers)
  - [Project Architecture](#project-architecture)
  - [Contact](#contact)

---

## Hardware & Tech Stack
* **Robot:** [Poppy Humanoid](https://www.poppy-project.org/) (25 Dynamixel servomotors)
* **Compute Node:** Raspberry Pi 5
* **Sensors & Peripherals:** 9DoF IMU, USB Audio Interface / Microphone & Speaker
* **Simulation:** CoppeliaSim
* **Language:** Python 3.x
* **Core Libraries:** `pypot`, `poppy-humanoid`, `opencv-python`, `PyQt5`, `openai`, `SpeechRecognition`, `pyttsx3`, `pygame`, `numpy`, `matplotlib`

---

## Quick Start: How to Run on Raspberry Pi 5

This framework runs directly on the Raspberry Pi 5 attached to the Poppy Humanoid.

### 1. Connection & Setup
Connect to the Raspberry Pi over an Ethernet cable via SSH:
```bash
ssh pi_username@<raspberry_pi_ip> (every username or password is "poppy")
```
*Note: If you need to install new packages or access external web APIs (such as OpenAI), ensure you share your host machine's internet connection over the Ethernet adapter.*

### 2. Activate the Virtual Environment
All dependencies are isolated within `robot_env`. Activate it before running any script:
```bash
source robot_env/bin/activate
```

### 3. Dependencies & System Packages
Core Python libraries are pre-installed in the virtual environment.

#### System-level TTS Engine (pyttsx3 Requirement)
Offline speech synthesis via `pyttsx3` requires Linux native speech packages:
```bash
sudo apt update
sudo apt install espeak espeak-ng libespeak1
```

#### Python Packages
If a package is missing or updated:
```bash
pip install -r requirements.txt
```

### 4. Running the Code
Select and run the script corresponding to the test or routine you wish to perform (see [Project Structure & Script Overview](#project-structure--script-overview)):
```bash
python InstantTestFolder/test_active_test_balance.py
```

---

## Emergency Stop & Reset Procedure

If a script terminates abruptly, is interrupted (`Ctrl+C`), or crashes during motor execution, the serial communication interfaces (`/dev/ttyACM*`) will remain locked by background handles. Follow this sequence before restarting any code:

### Step 1: Kill Hanging Processes and Free Serial Ports
Execute the following commands to kill lingering Python processes and clear the USB serial interfaces:
```bash
sudo pkill -9 -f python
sudo fuser -k /dev/ttyACM0
sudo fuser -k /dev/ttyACM1
```

### Step 2: Power Cycle the Motors
1. Disconnect the main DC power supply cable feeding the Dynamixel motor bus.
2. Wait 5 to 10 seconds for motor driver capacitors to discharge completely.
3. Reconnect the power supply.
4. Rerun your intended script safely.

---

## Project Structure & Script Overview

### Analysis
Scripts designed to validate mechanical and dynamic parameters between simulation and the physical robot:

* **`Analysis/StandUpTorqueAnalysis.py`**  
  Compares the joint torques required during a stand-up motion inside CoppeliaSim against the actual joint torques recorded on physical Dynamixel motors. Used to evaluate dynamic fidelity and motor load limits.

### PoppyTestGUI
A graphical control interface built with PyQt5:

* **`PoppyTestGUI/main.py`**  
  Connects to a running CoppeliaSim instance. Enables direct visual manipulation of motor positions, joint limit inspection, and rapid execution of predefined posture buttons without manual command-line calls.

### InstantTestFolder (Hardware & Feature Tests)
Dedicated standalone diagnostic and prototype routines:

* **`InstantTestFolder/MotorConnectionTests.py`**  
  Scans and pings all configured Dynamixel motor IDs across serial buses to confirm wiring, baud rates, and hardware availability.
* **`InstantTestFolder/MotorMovementsTest.py`**  
  Sends target position sequences to confirm that compliant modes are disabled and motors physically rotate as commanded.
* **`InstantTestFolder/IMUTestCodes.py`**  
  Connects to the IMU and prints raw accelerometer, gyroscope, and orientation readings to verify bus communication.
* **`InstantTestFolder/test_imu_balance_direction.py`**  
  Verifies IMU sign conventions and coordinate frame alignment relative to the torso coordinate frame to prevent inverted feedback loops during active balance.
* **`InstantTestFolder/test_active_test_balance.py`**  
  Implements closed-loop active balancing. It reads live pitch/roll data from the IMU and computes compensating angle offsets across `l_ankle`, `r_ankle`, `abs_y`, and `bust_y` motors simultaneously. *(Work in progress / experimental).*
* **`InstantTestFolder/TestVoiceCommands.py`**  
  Tests the complete speech interaction loop: captures microphone audio, listens for key triggers (e.g., `"hello"`), produces spoken audio feedback through the speaker, and commands the robot to perform a physical wave gesture.
* **`InstantTestFolder/FaceLCDTest.py`**  
  Driver test for an auxiliary LCD screen mounted on the head. (Hardware screen is currently not attached; script is preserved for future head display integration).
* **`InstantTestFolder/TestPoppy.py`**  
  Legacy interactive CLI test prompting the user for motor IDs and position inputs. *(Deprecated - use GUI or dedicated motor test scripts instead).*

### Controllers
Modular classes and wrappers abstracting hardware peripherals, safety mechanisms, and sensor pipelines:

* **`Controllers/RobotController.py`**  
  Main entry wrapper for robot lifecycle management. Handles connecting to the robot entity, initializing joint registers, setting operational speeds, and cleanly disconnecting.
* **`Controllers/MotorRelaxController.py`**  
  Hardware safety utility. Provides routines to safely make motors compliant (`compliant = True`) without mechanical drop shocks, as well as functions to forcibly detach motor power during abnormal conditions.
* **`Controllers/IMUController.py`**  
  Sensor interface class that manages serial/I2C communication with the IMU, applying calibration offsets, filtering raw noise, and returning formatted tilt data.
* **`Controllers/VoiceController.py`**  
  Coordinates speech recognition models and maps parsed natural language intents to corresponding robotic behaviors.
* **`Controllers/SpeakerController.py`**  
  Audio output abstraction managing sound file playback and text-to-speech engine invocations.
* **`Controllers/CameraController.py`**  
  Camera capture routines. Verified using host computer/webcam input; provides the base capture pipeline ready for mounting an onboard vision sensor on the robot.

---

## Project Architecture

The repository enforces separation between low-level hardware drivers, analytical evaluation scripts, and user interaction layers:

1. **Hardware Abstraction Layer (`Controllers/`):** Isolates low-level serial communication, safety cut-offs, audio I/O, and sensor streaming into reusable modules.
2. **Diagnostic & Motion Layer (`InstantTestFolder/`):** Provides focused scripts to test specific subsystems (motor connectivity, pitch feedback via torso/ankles, speech-gesture coordination) without starting a complex monolithic application.
3. **Simulation & Analysis (`PoppyTestGUI/`, `Analysis/`):** Connects to CoppeliaSim to benchmark joint torques against physical robot executions, mitigating mechanical failure risks on physical Dynamixel actuators.

---

## Contact

**Seyit Koyuncu**  
GitHub: [@SeyitKoyuncu](https://github.com/SeyitKoyuncu)
[@senembilgin](https://github.com/senembilgin)  
Repository: [PoppyHumanoidRobotProject](https://github.com/SeyitKoyuncu/PoppyHumanoidRobotProject)
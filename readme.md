# Poppy Humanoid Robot Project

A robust control and operation framework for the **Poppy Humanoid** robot, running directly on a **Raspberry Pi 5**. This repository contains the scripts, configurations, and environment setups required to drive the robot's motors, handle kinematics, and manage physical execution.

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
  - [Project Architecture](#project-architecture)
  - [Future Work](#future-work)
  - [Contact](#contact)

---

## Hardware & Tech Stack
* **Robot:** [Poppy Humanoid](https://www.poppy-project.org/)
* **Compute Node:** Raspberry Pi 5
* **Language:** Python 3.x
* **Core Libraries:** `pypot`, `poppy-humanoid`, `opencv-python`, `PyQt5`, `openai`, `speech_recognition`, `pyttsx3`, `pygame`

---

## Quick Start: How to Run on Raspberry Pi 5

This project is designed to execute directly on the Raspberry Pi 5 connected to the Poppy Humanoid. Follow the steps below to connect, activate the environment, and safely run the robot.

### 1. Connection & Setup
Connect to the Raspberry Pi via SSH using an Ethernet cable:
```bash
ssh pi_username@<raspberry_pi_ip>
```
*Note: If you need to download any new packages or updates, ensure you share your host machine's internet connection with the Raspberry Pi over the Ethernet interface.*

### 2. Activate the Virtual Environment
The code must be executed inside its dedicated virtual environment. Once connected via SSH, run:
```bash
source robot_env/bin/activate
```

### 3. Dependencies & System Packages
All core Python libraries are pre-installed in the virtual environment.

#### System-level TTS Engine (pyttsx3 Requirement)
The offline text-to-speech engine (`pyttsx3`) requires native system speech libraries to function properly on Linux / Raspberry Pi OS. If they are not already installed on the system, run:
```bash
sudo apt update
sudo apt install espeak espeak-ng libespeak1
```

#### Python Packages
If you modify the project or encounter a `ModuleNotFoundError`, install the missing modules via pip with active internet sharing:
```bash
pip install -r requirements.txt
```
Or install an individual package:
```bash
pip install <package_name>
```

### 4. Running the Code
Once the virtual environment is active, start the main control script:
```bash
python main.py
```
*(Note: Replace `main.py` with the specific entry point script if different).*

---

## Emergency Stop & Reset Procedure

If the program crashes, hangs, or is stopped abruptly during motor operation, serial communication ports may remain locked. Follow this procedure before restarting:

**Step 1: Terminate background processes and release serial ports**
Run the following commands to kill lingering Python processes and unlock the serial interfaces (`ttyACM0` and `ttyACM1`):
```bash
sudo pkill -9 -f python
sudo fuser -k /dev/ttyACM0
sudo fuser -k /dev/ttyACM1
```

**Step 2: Power Cycle the Motors**
1. Unplug the main power supply from the motor bus.
2. Wait 5 to 10 seconds to allow internal capacitors to discharge fully.
3. Reconnect the power supply.
4. Rerun the script.

---

## Project Architecture

*(Add a brief overview here explaining the project structure, such as kinematic control routines, balance loops, sensory feedback processing, and GUI/voice interaction pipelines).*

---

## Future Work

- [ ] Implement advanced dynamic balancing algorithms.
- [ ] Add real-time IMU feedback integration.
- [ ] Optimize autonomous speech and vision feedback loops.

---

## Contact

**Seyit Koyuncu**  
GitHub: [@SeyitKoyuncu](https://github.com/SeyitKoyuncu)  
Project Repository: [PoppyHumanoidRobotProject](https://github.com/SeyitKoyuncu/PoppyHumanoidRobotProject)
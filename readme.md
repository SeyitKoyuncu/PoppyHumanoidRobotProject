For connecting to popy with ssh:

ssh poppy@poppy.local
password: poppy

source robot_env/bin/activate -> activate virtual environment

./robot_env/bin/python -m pip install pypot

sudo pkill -9 -f python
sudo fuser -k /dev/ttyACM0

from pypot.creatures import PoppyHumanoid
poppy = PoppyHumanoid()
poppy.head_z.goal_position = 20

## TODO

05/12/2026
Software Setup & Troubleshooting:
The Jupyter setup is currently throwing an error. We will reinstall it on Poppy and try accessing it through the browser again. If the error persists, we will try using JupyterLite. Should JupyterLite fail as well, we will switch to VS Code with Remote SSH.

Hardware & Motor Control:
We are currently unable to control the motors due to the insufficient 5V power supply. We need to switch to a 12V power supply using a capable power cable. The system will be tested next with 12V.

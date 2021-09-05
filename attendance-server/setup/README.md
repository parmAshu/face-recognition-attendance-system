# Setup Attendance Server

The attendance server can be used in two ways -
1. The program can be deployed on a central server within the campus's local network. In this case all the AI-enabled camera devices will communicate with this server over the local network.
2. If the system is not be integrated with existing systems or the number of employees is less then, both the attendance server and the face-recognition program can be deployed on the AI-camera machine itself ( this machine must be a SBC running linux based OS.)

# Installing dependencies

1. Install python3 (if not already installed)
2. Install required python packages.These packages are mentioned in requirements.txt file. Installing can be done using the command : <br> 
`pip3 install -r requirements.txt`
3. Install mongodb and enable. User the following commands for installing on raspbian: <br>
`sudo apt install mongodb`<br>
`sudo systemctl enable mongodb`<br>
`sudo systemctl start mongdb`<br>
4. Now generate the service file and environment variable file by executing the `generateServiceFile.py` script from the `setup` directory.
5. Test the attendance server using the following command : <br>
`source <project-path>/attendance-server/setup/env_vars.sh` <br>
`python3 <project-path>/attendance-server/src/run.py`
6. If there are any errors then rectify them before proceeding to next step
7. This step is valid only for machines having `systemd`. Move the `attendanceServer.service` file to systemd service file directory and use the following commands to active it:<br>
`systemctl enable attendanceServer.service`
`systemctl start attendanceServer.service`
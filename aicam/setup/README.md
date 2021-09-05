# Setup instructions for aicam

AIcam software is peforms the face-recognition and marks attendance using the APIs provided by the attendance-server

# Installing Dependencies

1. Install python3 (if not already installed.)
2. Now install all the required python packages. This can be done using the following command : <br>
`pip3 install -r requirements.txt`

# Deploying Software

1. Now generate the service file using the command `python3 generateServiceFile.py`. This will generate the service file and environment variable file. The command must be run from the setup directory.
2. Test the program by executing the command `python3 <project-path>/aicam/src/app.py`. If there are any errors then rectify them before proceeding to next step.
3. Now, deploy the service by putting the `aicam.service` file in the systemd service file directory and executing the following commands : <br>
`systemctl enable aicam.service` <br>
`systemctl start aicam.service`

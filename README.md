# Jerry
Control System for running and controlling Jerry the minibot. <br>
Client.py contains all client code. <br>
Server.py contains all server and robot code. <br>
Classes.py contains shared code and constants. <br>

## Running
The server will automatically start up on Jerry and to gain control just run Client.py and have a joystick plugged in. Right now the client won't connect until a controller is plugged in.

## Building/Deploying
All of the packages should be in requirements.txt. <br>
`pip install -r requirements.txt` <br>
### runServerCommands.py
Use this to perform various operations on the py. <br>
Flags: <br>
`-u` - Uploads new files to the pi. Must be specfied in the file right now its Server.py and Classes.py<br>
`-k` - Kills all python programs on the py. Should use this when uploading files.<br>
`-p` - Runs the pigpio daemon on the pi to allow interacting with gpio.<br>
`-r` - Runs the Server.py file to start the code.<br>
eg. `py runServerCommands.py -k -u -r` will kill the python program, upload new files to the pi and run them.

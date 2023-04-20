import socket
import traceback

import pigpio
from Classes import Constants, JoystickData

pi = pigpio.pi() 
server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
motorFR = Constants.talonSignalPins[0]
motorFL = Constants.talonSignalPins[1]
motorBR = Constants.talonSignalPins[2]
motorBL = Constants.talonSignalPins[3]
# motors = (motorFR, motorFL, motorBR, motorBL)
motors = (motorFR, )
robotEnabled = False

ip = Constants.listenIP
port = Constants.port
address = (ip, port)

server.bind(address)
server.listen(5)

def getClampingFactor(input: list[float]) -> float:
    absNums = [abs(num) for num in input]
    if (max(absNums) <= 1): return 1
    return (1/max(absNums))

def drive(input: JoystickData):
    # servos use pulsewidth, talon srx full reverse is 1 ms, full forward is 2 ms, neutral is 1.5 ms
    # throttle = (input.axis1 / 2 + 0.5) * 1000 + 1000 # transform range from -1 to 1 into 1000 to 2000 (microseconds)
    ySpeed = input.yAxis
    xSpeed = input.xAxis
    turn = input.twist
    motorSpeeds = [ySpeed, ySpeed, ySpeed, ySpeed]
    factor = getClampingFactor(motorSpeeds)
    factored = [factor * n for n in motorSpeeds]
    print(factored)
    for i in range(len(motors)):
        pi.set_servo_pulsewidth(motors[i], toPulseWidth(motorSpeeds[i] * factor))
        
def toPulseWidth(val):
    '''Converts from the range -1 to 1 into the range 1000 to 2000'''
    return (val / 2 + 0.5) * 1000 + 1000
        
def stop():
    for motor in motors:
        pi.set_servo_pulsewidth(motor, 0)

def main():
    global robotEnabled
    try:
        while True:
            print("Waiting for Connection . . .")
            client, clientAddress = server.accept()
            print("Connection Created with " + str(clientAddress))
            try: 
                client.settimeout(Constants.clientTimeoutSec)
                while True:
                    bufLength = int.from_bytes(client.recv(1), "big")
                    if (bufLength <= 0): continue
                    buf = client.recv(bufLength)
                    msg = buf.decode()
                    if msg.__eq__(Constants.socketClose):
                        break
                    elif msg.__eq__(Constants.enabledMsg):
                        print("Enabled")
                        robotEnabled = True
                    elif msg.__eq__(Constants.disabledMsg):
                        print("Disabled")
                        robotEnabled = False
                    else:
                        data = JoystickData.fromRaw(buf)
                        if robotEnabled:
                            drive(data)
            except socket.timeout as error:
                print("Connection Interrupted: " + str(error))
            finally:
                stop() # stops every time socket loses connection or is closed
                robotEnabled = False
                print("Client Closed.")
                client.close()
    finally:
        stop()
        print("Server Closed.")
        server.close()

if __name__ == "__main__" :
    for motor in motors:
        pi.set_PWM_frequency(motor, Constants.talonFrequencyHz)
    main()
    
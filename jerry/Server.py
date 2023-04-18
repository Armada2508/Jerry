#!/usr/bin/python3.11
import socket
import traceback

import pigpio
from Classes import Constants, JoystickData

pi = pigpio.pi() 
sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

sock.bind(address)
sock.listen(5)

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
    for i in range(4):
        pi.set_servo_pulsewidth(motors[i], motorSpeeds[i] * factor)
        
def stop():
    for motor in motors:
        pi.set_servo_pulsewidth(motor, 0)

def main():
    global robotEnabled
    while True:
        print("Waiting for Connection . . .")
        client, clientAddress = sock.accept()
        print("Connection Created with " + str(clientAddress))
        try: 
            client.settimeout(Constants.clientTimeoutSec)
            while True:
                bufLength = int(client.recv(2))
                buf = client.recv(bufLength)
                msg = buf.decode()
                if msg.__eq__(Constants.socketClose):
                    break
                elif msg.__eq__(Constants.enabledMsg):
                    robotEnabled = True
                elif msg.__eq__(Constants.disabledMsg):
                    robotEnabled = False
                data = JoystickData.fromRaw(buf)
                if robotEnabled:
                    drive(data)
        except TimeoutError as error:
            print("Connection Interrupted: " + str(error))
            traceback.print_exc()
        finally:
            stop() # stops every time socket loses connection or is closed
            robotEnabled = False
            print("Client Closed.")
            client.close()

if __name__ == "__main__" :
    for motor in motors:
        pi.set_PWM_frequency(motor, Constants.talonFrequencyHz)
    main()
    
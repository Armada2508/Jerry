import socket
import time
from threading import Thread

import pigpio
from Classes import Constants, JoystickData
from Gyro import Gyro

pi = pigpio.pi() 
server: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# gyro = Gyro(Constants.gyroDegreeDeadband)
# anglePollThread = Thread(target = gyro.updateAngleContinuously, name = "Gyro Updater")
motorFR = Constants.talonSignalPins[0]
motorFL = Constants.talonSignalPins[1]
motorBR = Constants.talonSignalPins[2]
motorBL = Constants.talonSignalPins[3]
motors = [motorFR, motorFL, motorBR, motorBL]
invertedMotors = [motorFR, motorBL]
robotEnabled = False

ip = Constants.listenIP
port = Constants.port
address = (ip, port)

server.bind(address)
server.listen(5)

def getPowerFactor(input: list[float]) -> float:
    absNums = [abs(num) for num in input]
    if (max(absNums) <= 1): return 1
    return (1/max(absNums))

def drive(input: JoystickData):
    ySpeed = input.yAxis
    xSpeed = input.xAxis
    turn = input.twist
    # Deadband
    ySpeed = clampDeadband(ySpeed, Constants.joystickDeadband)
    xSpeed = clampDeadband(xSpeed, Constants.joystickDeadband)
    turn = clampDeadband(turn, Constants.turnDeadband) * Constants.turnFactor
    # Drive Mecanum
    motorSpeeds = [
        ySpeed - xSpeed - turn, #FR
        ySpeed + xSpeed + turn, #FL
        ySpeed + xSpeed - turn, #BR
        ySpeed - xSpeed + turn  #BL
    ]
    # Getting factor to normalize everything so that the max is Constants.speedFactor and everything else is below that
    factor = getPowerFactor(motorSpeeds)
    for i in range(len(motors)):
        speed = motorSpeeds[i] * factor
        # Check for inverted motors
        if invertedMotors.__contains__(motors[i]): speed *= -1
        speed *= Constants.speedFactor
        pi.set_servo_pulsewidth(motors[i], toPulseWidth(speed))
        
def clampDeadband(speed: float, deadband: float):
    return 0 if (abs(speed) < deadband) else speed
        
def toPulseWidth(val: float):
    '''Converts from the range -1 to 1 into the range 1000 to 2000'''
    return (val / 2 + 0.5) * 1000 + 1000

def flashRSL():
    global flashTimer
    gpio = Constants.RSLRPin
    if (robotEnabled):
        val = 0 if pi.read(gpio) == 1 else 1
        pi.write(gpio, val)
    else:
        pi.write(gpio, 0)
        
def RSLLoop():
    while True:
        flashRSL()
        time.sleep(Constants.RSLFLashTime)
        
def stop():
    for motor in motors:
        pi.set_servo_pulsewidth(motor, 0)

def main():
    global robotEnabled
    # Setup RSL Light
    pi.write(Constants.RSLWPin, 1)
    pi.write(Constants.RSLRPin, 0)
    try:
        while True:
            print("Waiting for Connection . . .")
            client, clientAddress = server.accept()
            print("Connection Created with " + str(clientAddress))
            try: 
                client.settimeout(Constants.clientTimeoutSec)
                while True:
                    # print("Angle: " + str(gyro.getAngle() % 360))
                    bufLength = int.from_bytes(client.recv(1), "big")
                    if (bufLength <= 0): continue
                    buf = client.recv(bufLength)
                    msg = buf.decode()
                    if msg.__eq__(Constants.socketClose):
                        break
                    elif msg.__eq__(Constants.enabledMsg):
                        robotEnabled = True
                        print("Enabled")
                    elif msg.__eq__(Constants.disabledMsg):
                        stop()
                        robotEnabled = False
                        print("Disabled")
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
    # anglePollThread.start()
    flashRSLThread = Thread(target = RSLLoop, name = "RSL Flasher")
    flashRSLThread.start()
    main()
    
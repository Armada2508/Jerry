import socket
import traceback

import pigpio
from Data import Constants, JoystickData

pi = pigpio.pi() 
sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
motors = Constants.talonSignalPins
robotEnabled = False

ip = Constants.listenIP
port = Constants.port
address = (ip, port)

sock.bind(address)
sock.listen(5)

def drive(input: JoystickData):
    throttle = (input.axis1 / 2 + 0.5) * 1000 + 1000 # transform range from -1 to 1 into 1000 to 2000 (microseconds)
    print(throttle)
    for motor in motors:
        # servos use pulsewidth, talon srx full reverse is 1 ms, full forward is 2 ms, neutral is 1.5 ms
        pi.set_servo_pulsewidth(motor, throttle)
        
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
                match buf.decode():
                    case Constants.socketClose: 
                        break
                    case Constants.enabledMsg:
                        robotEnabled = True
                    case Constants.disabledMsg:
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
    
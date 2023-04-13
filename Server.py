import os
import socket
import traceback

import pigpio

from Data import JoystickData

pi = pigpio.pi() 
sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
motors = [5]

ip = "0.0.0.0"
port = 13505

sock.bind((ip, port))
sock.listen(5)

for motor in motors:
    pi.set_PWM_frequency(motor, 1000)
    pi.set_PWM_range(motor, 100)

def drive(input: JoystickData):
    throttle = (input.axis1 / 2 + 0.5) * 100  # transform range from -1 to 1 into 0 to 100
    print(throttle)
    for motor in motors:
        pi.set_PWM_dutycycle(motor, throttle)
        
def stop():
    for motor in motors:
        pi.set_PWM_dutycycle(motor, 0)

def main():
    while True:
        print("Waiting for Connection . . . ")
        client, address = sock.accept()
        print("Connection Created with " + str(address))
        try: 
            while True:
                bufLength = int(client.recv(2).decode())
                buf = client.recv(bufLength)
                if (buf.decode() == "Socket Closed"):
                    stop()
                    break
                data = JoystickData.fromRaw(buf)
                drive(data)
        except Exception:
            print("Connection Interrupted.")
            traceback.print_exc()
            client.close()
            pass

if __name__ == "__main__" :
    main()
    
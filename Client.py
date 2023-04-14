import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import socket
import time

import pygame
from pygame import joystick

from Data import JoystickData

pygame.init()
joystick.init()

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "raspberrypi.local"
port = 13505
address = (ip, port)

def main():
    while joystick.get_count() < 1:
        pygame.event.pump()
        pass
    controller: joystick.JoystickType = joystick.Joystick(0)
    print("Controller: {}, ID: {}, Axis: {}, Buttons: {}".format(controller.get_name(), controller.get_instance_id(), controller.get_numaxes(), controller.get_numbuttons()))
    print("Connecting . . .")
    conn = sock.connect_ex(address)
    if (conn == 0):
        print("Successfully connected to " + str(address))
        try:
            while True:
                pygame.event.pump()
                currentPacket = JoystickData( controller.get_instance_id(),
                    controller.get_axis(0), controller.get_axis(1) * -1, controller.get_axis(2), controller.get_axis(3),
                    controller.get_button(0), controller.get_button(1), controller.get_button(2), controller.get_button(3),
                    controller.get_button(4), controller.get_button(5), controller.get_button(6), controller.get_button(7),
                    controller.get_button(8), controller.get_button(9), controller.get_button(10), controller.get_button(11),
                )
                raw = currentPacket.toRaw()
                sock.send(str(len(raw)).encode())
                sock.send(raw)
                time.sleep(0.05)
        except BaseException as e:
            try: 
                msg = "Socket Closed"
                sock.send(str(len(msg)).encode())
                sock.send(msg.encode())
            except Exception: 
                pass
            print("Connection Closed. " + str(e))
            pass
    else:
        print("Socket Connection Failed. " + str(conn))
        pass
    print("Closing Socket.")
    sock.close()
    joystick.quit()
    pygame.quit()
    
if __name__ == "__main__" :
    main()
    

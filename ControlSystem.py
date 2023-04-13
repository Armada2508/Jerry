import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import socket

import pygame
from pygame import joystick

from Data import JoystickData

pygame.init()
joystick.init()

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ip = "raspberrypi.local"
ip = "localhost"
port = 13505

def main():
    while joystick.get_count() < 1:
        pygame.event.pump()
        pass
    controller: joystick.JoystickType = joystick.Joystick(0)
    print("Controller: {}, ID: {}, Axis: {}, Buttons: {}".format(controller.get_name(), controller.get_instance_id(), controller.get_numaxes(), controller.get_numbuttons()))
    print("Connecting . . .")
    conn = sock.connect_ex((ip, port))
    if (0 == 0):
        try:
            while True:
                pygame.event.pump()
                currentPacket = JoystickData( controller.get_instance_id(),
                    controller.get_axis(0), controller.get_axis(1), controller.get_axis(2), controller.get_axis(3),
                    controller.get_button(0), controller.get_button(1), controller.get_button(2), controller.get_button(3),
                    controller.get_button(4), controller.get_button(5), controller.get_button(6), controller.get_button(7),
                    controller.get_button(8), controller.get_button(9), controller.get_button(10), controller.get_button(11),
                )
                sock.send(currentPacket.toRaw())
        except BaseException as e:
            try: sock.send("Socket Closed".encode())
            except: pass
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
    

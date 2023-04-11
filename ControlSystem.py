import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import socket

import pygame
from pygame import joystick

from Data import JoystickData

pygame.init()
joystick.init()

controller: joystick.JoystickType = joystick.Joystick(0)
print("Controller: {}, ID: {}, Axis: {}, Buttons: {}".format(controller.get_name(), controller.get_instance_id(), controller.get_numaxes(), controller.get_numbuttons()))

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "raspberrypi.local"
port = 13505

def main():
    print("Connecting . . .")
    conn = sock.connect_ex((ip, port))
    if (conn == 0):
        try:
            while True:
                sock.send(input("Input: ").encode())
                print(sock.recv(4096).decode())
                # pygame.event.get()
                # currentPacket = JoystickData( controller.get_instance_id(),
                #     controller.get_axis(0), controller.get_axis(1), controller.get_axis(2), controller.get_axis(3),
                #     controller.get_button(0), controller.get_button(1), controller.get_button(2), controller.get_button(3),
                #     controller.get_button(4), controller.get_button(5), controller.get_button(6), controller.get_button(7),
                #     controller.get_button(8), controller.get_button(9), controller.get_button(10), controller.get_button(11),
                # )
                # print(currentPacket)
                # os.system("cls")
                # sock.send(currentPacket.toRaw())
        except Exception as e:
            print("Connection Closed. " + str(e))
            pass
    else:
        print("Socket Connection Failed. " + str(conn))
        pass
    sock.close()
    joystick.quit()
    pygame.quit()
    
if __name__ == "__main__" :
    main()
    

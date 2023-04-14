import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import socket
import time

import pygame
from pygame import joystick

from Data import Constants, JoystickData

pygame.init()
joystick.init()

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = Constants.rpiIP
port = Constants.port
address = (ip, port)

def bLen(obj):
    return bytes(len(obj))

def shutdown():
    print("Closing Socket.")
    sock.close()
    joystick.quit()
    pygame.quit()

def main():
    print("Waiting for a joystick to be connected . . .")
    while joystick.get_count() < 1:
        pygame.event.pump()
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
                sock.send(bLen(raw))
                sock.send(raw)
                time.sleep(Constants.clientSleepSec)
        finally:
            try: 
                msg = Constants.socketClose
                sock.send(bLen(msg))
                sock.send(msg.encode())
            except Exception as error: 
                print("Couldn't send close message: " + str(error))
                pass
            print("Connection Closed.")
            shutdown()
    else:
        print("Socket Connection Failed. " + str(conn))
    shutdown()
    
    
if __name__ == "__main__" :
    main()
    

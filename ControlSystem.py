import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from pygame import joystick

from Data import JoystickData

pygame.init()
joystick.init()

controller: joystick.JoystickType = joystick.Joystick(0)
print("Controller: {}, ID: {}, Axis: {}, Buttons: {}".format(controller.get_name(), controller.get_instance_id(), controller.get_numaxes(), controller.get_numbuttons()))


def main():
    while True:
        print(controller.get_button(11))
        currentPacket = JoystickData( controller.get_instance_id(),
            controller.get_axis(0), controller.get_axis(1), controller.get_axis(2), controller.get_axis(3),
            controller.get_button(0), controller.get_button(1), controller.get_button(2), controller.get_button(3),
            controller.get_button(4), controller.get_button(5), controller.get_button(6), controller.get_button(7),
            controller.get_button(8), controller.get_button(9), controller.get_button(10), controller.get_button(11),
        )
        # print(currentPacket)
        # os.system("cls")
    
    
if __name__ == "__main__" :
    main()
    

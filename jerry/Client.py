import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import socket
import time
from multiprocessing import Process, Value
from tkinter import Button, Tk

import pygame
from Data import Constants, JoystickData
from pygame import joystick

pygame.init()
joystick.init()

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = Constants.rpiIP
port = Constants.port
address = (ip, port)

socketConnected = Value('b', False)
robotEnabled = Value('b', False)

def bLen(obj):
    '''Used to figure out how many bytes the data you want to send is.'''
    return bytes(len(obj))

def updateEnabled(bool):
    '''You can't assign variables in lambdas.'''
    global robotEnabled
    robotEnabled.value = bool
    
def stopProgram(root: Tk, proc: Process):
    root.destroy()
    proc.terminate()

def cleanup():
    '''Clean up resources, tell server socket was closed if ever connected.'''
    global socketConnected
    if socketConnected.value:
        try: 
            msg = Constants.socketClose
            sock.send(bLen(msg))
            sock.send(msg.encode())
        except Exception as error: 
            print("Couldn't send close message: " + str(error))
        print("Connection Closed.")
        socketConnected.value = False
    print("Closing Socket.")
    sock.close()
    joystick.quit()
    pygame.quit()

def main(enabled, connected):
    print("Waiting for a joystick to be connected . . .")
    while joystick.get_count() < 1:
        pygame.event.pump()
    controller: joystick.JoystickType = joystick.Joystick(0)
    print("Controller: {}, ID: {}, Axis: {}, Buttons: {}".format(controller.get_name(), controller.get_instance_id(), controller.get_numaxes(), controller.get_numbuttons()))
    while True:
        print("Connecting . . .")
        conn = sock.connect_ex(address)
        if (conn == 0):
            connected.value = True
            print("Successfully connected to " + str(address))
            lastVal = False
            while True:
                pygame.event.pump()
                currentPacket = JoystickData( controller.get_instance_id(),
                    controller.get_axis(0), controller.get_axis(1) * -1, controller.get_axis(2), controller.get_axis(3),
                    controller.get_button(0), controller.get_button(1), controller.get_button(2), controller.get_button(3),
                    controller.get_button(4), controller.get_button(5), controller.get_button(6), controller.get_button(7),
                    controller.get_button(8), controller.get_button(9), controller.get_button(10), controller.get_button(11),
                )
                if (enabled.value != lastVal):
                    msg = Constants.enabledMsg if enabled.value else Constants.disabledMsg
                    sock.send(bLen(msg))
                    sock.send(msg)
                rawData = currentPacket.toRaw()
                sock.send(bLen(rawData))
                sock.send(rawData)
                time.sleep(Constants.clientSleepSec)
                lastVal = enabled.value
        else:
            print("Socket Connection Failed. " + str(conn))
    
if __name__ == "__main__" :
    try:
        root = Tk()
        root.title("Bootleg Driver Station")
        eButton = Button(root, text = "Enable", command = lambda: updateEnabled(True))
        dButton = Button(root, text = "Disable", command = lambda: updateEnabled(False))
        eButton.pack()
        dButton.pack()
        controlLoop = Process(target = main, args = (robotEnabled, socketConnected), name = "Main Loop")
        controlLoop.start()
        root.protocol("WM_DELETE_WINDOW", lambda: stopProgram(root, controlLoop))
        root.mainloop()
    finally:
        cleanup()
    
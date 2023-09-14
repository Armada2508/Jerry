import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import socket
import sys
import time
from tkinter import Button, Frame, Label, Tk

import pygame
from Classes import Constants, JoystickData, StoppingThread
from pygame import joystick
from pynput import keyboard

pygame.init()
joystick.init()

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = Constants.rpiIP
port = Constants.port
address = (ip, port)

robotStatusLabel: Label
joystickStatusLabel: Label
connectionStatusLabel: Label

socketConnected = False
robotEnabled = False

def bLen(obj) -> bytes:
    '''Used to figure out how many bytes the data you want to send is.'''
    return int.to_bytes(len(obj))

def updateEnabled(bool):
    '''You can't assign variables in lambdas.'''
    global robotEnabled
    robotEnabled = bool
    txt = Constants.enabledMsg if robotEnabled else Constants.disabledMsg
    fg = "Green" if robotEnabled else "Red"
    robotStatusLabel.config(text = "Robot Status: " + txt, foreground = fg)
    
def stopProgram(root: Tk, thread, listen):
    thread.stop()
    listen.stop()
    root.destroy()
    
def cleanup():
    '''Clean up resources, tell server socket was closed if ever connected.'''
    if socketConnected:
        try: 
            msg = Constants.socketClose
            sock.send(bLen(msg))
            sock.send(msg.encode())
        except Exception as error: 
            print("Couldn't send close message: " + str(error))
        print("Connection Closed.")
    print("Closing Socket.")
    sock.close()
    joystick.quit()
    pygame.quit()
        
def listen(key):
    global robotEnabled
    if key == keyboard.Key.enter:
        updateEnabled(False)
    
def main(self: StoppingThread):
    global socketConnected, sock
    while True:
        joystickStatusLabel.config(text = "Controller Disconnected", foreground = "Red")
        connectionStatusLabel.config(text = "Not Connected to Robot", foreground = "Red")
        print("Waiting for a joystick to be connected . . .")
        pygame.event.pump()
        while joystick.get_count() < 1:
            if self.stopped:
                return
            pygame.event.pump()
        controller: joystick.JoystickType = joystick.Joystick(0)
        print("Controller: {}, ID: {}, Axis: {}, Buttons: {}".format(controller.get_name(), controller.get_instance_id(), controller.get_numaxes(), controller.get_numbuttons()))
        joystickStatusLabel.config(text = "Controller Connected", foreground = "Green")
        try:
            print("Connecting . . .")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn = sock.connect_ex(address)
            if (conn == 0):
                socketConnected = True
                print("Successfully connected to " + str(address))
                lastVal = False
                connectionStatusLabel.config(text = "Connected to Robot", foreground = "Green")
                while True:
                    if self.stopped:
                        return
                    pygame.event.pump()
                    if (joystick.get_count() < 1):
                        updateEnabled(False)
                        msg = Constants.disabledMsg
                        sock.send(bLen(msg))
                        sock.send(msg.encode())
                        break
                    currentPacket = JoystickData( controller.get_instance_id(),
                        controller.get_axis(0), controller.get_axis(1) * -1, controller.get_axis(2), controller.get_axis(3),
                        controller.get_button(0), controller.get_button(1), controller.get_button(2), controller.get_button(3),
                        controller.get_button(4), controller.get_button(5), controller.get_button(6), controller.get_button(7),
                        controller.get_button(8), controller.get_button(9), controller.get_button(10), controller.get_button(11),
                    )
                    current = robotEnabled
                    if (current != lastVal):
                        lastVal = current
                        msg = Constants.enabledMsg if current else Constants.disabledMsg
                        sock.send(bLen(msg))
                        sock.send(msg.encode())
                    rawData = currentPacket.toRaw()
                    sock.send(bLen(rawData))
                    sock.send(rawData)
                    time.sleep(Constants.clientSleepSec)
            else:
                print("Socket Connection Failed. " + str(conn))
        except Exception as e:
            print("Connection Stopped: " + str(e))
            
def setupGUI(root: Tk):
    global robotStatusLabel, joystickStatusLabel, connectionStatusLabel
    width = root.winfo_screenwidth()
    height = 250
    x = 0-8
    y = root.winfo_screenheight()-height
    root.title("Bootleg Driver Station")
    root.geometry("{}x{}+{}+{}".format(width, height, x, y))
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.bind("<Configure>", lambda event: root.geometry("+{}+{}".format(x, y))),
    buttonLayout = Frame(root)
    eButton = Button(root, text = "Enable", command = lambda: updateEnabled(True), width = 20, height = 3, font = ("Ariel", 15))
    dButton = Button(root, text = "Disable", command = lambda: updateEnabled(False), width = 20, height = 3, font = ("Ariel", 15))
    robotStatusLabel = Label(root, text = "Robot Status: " + Constants.disabledMsg, font = ("Ariel", 28), foreground = ("Red"))
    joystickStatusLabel = Label(root, text = "Controller Disconnected", font = ("Ariel", 20), foreground = ("Red"))
    connectionStatusLabel = Label(root, text = "Not Connected to Robot", font = ("Ariel", 20), foreground = ("Red"))
    buttonLayout.pack(side="top")
    eButton.pack(in_=buttonLayout, side="left")
    dButton.pack(in_=buttonLayout, side="right")
    robotStatusLabel.pack()
    connectionStatusLabel.pack()
    joystickStatusLabel.pack()
    
if __name__ == "__main__":
    try:
        root = Tk()
        if (not sys.argv.__contains__("nogui")):
            setupGUI(root)
        controlLoop = StoppingThread(target = main, name = "Main Loop")
        controlLoop.giveSelfToTarget()
        controlLoop.start()
        enterListener = keyboard.Listener(on_press=listen)
        enterListener.start()   
        root.protocol("WM_DELETE_WINDOW", lambda: stopProgram(root, controlLoop, enterListener))
        root.mainloop()
    except KeyboardInterrupt:
        stopProgram(root, controlLoop, enterListener)
    finally:
        cleanup()
    
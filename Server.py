import os
import socket
import time

from Data import JoystickData

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "0.0.0.0"
port = 13505

sock.bind((ip, port))
sock.listen(5)

def main():
    while True:
        print("Waiting for Connection . . . ")
        client, address = sock.accept()
        print("Connection Created with " + str(address))
        try: 
            while True:
                buf = client.recv(1024)
                if (buf.decode() == "Socket Closed"):
                    break
                data = JoystickData.fromRaw(buf)
                os.system("clear")
                print(data)
                time.sleep(0.05)
        except Exception as e:
            print("Connection Interrupted. " + str(e))
            client.close()
            pass

if __name__ == "__main__" :
    main()
    
import os
import socket
import traceback

from Data import JoystickData

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "0.0.0.0"
port = 13505

sock.bind((ip, port))
sock.listen(5)

def main():
    clear = "clear"
    if os.name == "nt":
        clear = "cls"
    while True:
        print("Waiting for Connection . . . ")
        client, address = sock.accept()
        print("Connection Created with " + str(address))
        try: 
            while True:
                bufLength = int(client.recv(2).decode())
                buf = client.recv(bufLength)
                if (buf.decode() == "Socket Closed"):
                    break
                data = JoystickData.fromRaw(buf)
                os.system(clear)
                print(data)
        except Exception:
            print("Connection Interrupted.")
            traceback.print_exc()
            client.close()
            pass

if __name__ == "__main__" :
    main()
    
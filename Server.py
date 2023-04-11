import socket
import time

sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

ip = "0.0.0.0"
port = 13505

sock.bind((ip, port))
sock.listen(5)

def main():
    print("Waiting for Connection . . . ")
    client, address = sock.accept()
    print("Connection Created with " + str(address))
    try: 
        while True:
            buf = client.recv(4096)
            client.send(buf)
    except Exception as e:
        print("Connection Interrupted. " + str(e))
        pass
    client.close()
    time.sleep(1)
    main()

if __name__ == "__main__" :
    main()
    
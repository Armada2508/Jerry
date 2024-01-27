import sys

import fabric

from Hidden import password

# host = "raspberrypi.local"
host = "10.25.8.94"

def main():
    args = sys.argv
    c = fabric.Connection(host, port=22, user="raspberry", connect_kwargs={'password': password}, connect_timeout=10)
    c.open()
    print("Connected!")
    if (args.__contains__('-k')):
        print("Killing python processes . . .")
        c.run("sudo pkill python", warn=True)
        print("Finished killing processes.")

    if (args.__contains__("-u")):
        print("Uploading Files . . .")
        c.put("jerry/Server.py", "Jerry/")
        c.put("jerry/Classes.py", "Jerry/")
        c.put("jerry/Gyro.py", "Jerry/")
        print("Finished Upload.")
        
    if (args.__contains__("-p")):
        print("Attempting to start pigpiod daemon.")
        c.run("sudo pigpiod")

    if (args.__contains__("-r")):
        with c.cd("~/Jerry/"):
            print("Running Server . . .")
            print("Python Output Below.\n")
            c.run("python Server.py", pty=True, warn=True)
    c.close()
    
if __name__ == "__main__":
    main()
    
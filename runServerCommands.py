import sys

import fabric
from fabric.transfer import Transfer
from invoke import UnexpectedExit

from Hidden import password

# host = "raspberrypi.local"
host = "10.25.8.94"

def main():
    args = sys.argv
    c = fabric.Connection(host, port=22, user="raspberry", connect_kwargs={'password': password})
    c.open()
    print("Connected!")
    if (args.__contains__('-k')):
        print("Killing python processes . . .")
        try:
            c.run("sudo pkill python")
        except UnexpectedExit as e:
            print("No python processes running." + "\n" + str(e))
        print("Finished killing processes.")

    if (args.__contains__("-u")):
        fileTransfer = Transfer(c)
        print("Uploading Files . . .")
        fileTransfer.put("jerry/Server.py", "Jerry/")
        fileTransfer.put("jerry/Classes.py", "Jerry/")
        print("Finished Upload.")
        
    if (args.__contains__("-p")):
        print("Attempting to start pigpiod daemon.")
        c.run("sudo pigpiod")

    if (args.__contains__("-r")):
        with c.cd("~/Jerry/"):
            print("Running Server . . .")
            print("SERVER OUTPUT BELOW.\n")
            c.run("python Server.py")
    c.close()
    
if __name__ == "__main__":
    main()
    
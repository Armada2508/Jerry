import sys

import fabric
from fabric.transfer import Transfer

from Hidden import password


def main():
    args = sys.argv
    c = fabric.Connection("raspberrypi.local", port=22, user="raspberry", connect_kwargs={'password': password})
    
    if (args.__contains__('-k')):
        print("Killing python processes . . .")
        c.run("pkill python")
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

    with c.cd("~/Jerry/"):
        print("Running Server . . .")
        print("SERVER OUTPUT BELOW.\n")
        c.run("python Server.py")
    c.close()
    
if __name__ == "__main__":
    main()
    
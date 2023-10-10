import time

import spidev  # Linux only

spi = spidev.SpiDev()
spi.open(0, 0)

# Settings
spi.max_speed_hz = 8080000
spi.lsbfirst = False
spi.mode = 0b00

def sleep():
    time.sleep(0.005) # 5 ms

def printResp(resp):
    for byte in resp:
        print(format(byte, "#010b"))

def getSensorData(chk = False):
    sensorDataCHK = [0x30, 0x00, 0x00, 0x02]
    sensorData = [0x30, 0x00, 0x00, 0x01]
    msg = sensorDataCHK if chk else sensorData
    spi.writebytes(msg)
    sleep()
    return spi.readbytes(4)

def getAngularRate(data):
    # Returns angular rate in degrees per second
    rate = data[0] & 0x03
    rate = (rate << 2) | data[1] 
    rate = (rate << 8) | data[2]
    rate = rate >> 2

    # two's complement
    rate /= 80.0 # convert from rate data to degrees per second
    return rate
    
def startupSequence():
    resp = spi.readbytes(4)
    printResp(resp)
    getSensorData(True)
    getSensorData() # FF || EE
    getSensorData() # FF || EE
    
# startupSequence()
# print("\nEnd Startup Sequence\n")
while True:
    rate = getAngularRate(getSensorData())
    print(str(rate) + " degrees per second.")
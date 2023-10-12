import ctypes
import time

import spidev  # Linux only

# https://www.analog.com/media/en/technical-documentation/data-sheets/ADXRS450.pdf

# SPI
spi = spidev.SpiDev()
spi.open(0, 0)

# SPI Settings
spi.max_speed_hz = 8080000
spi.lsbfirst = False
spi.mode = 0b00

def printResp(resp):
    for byte in resp:
        print(format(byte, "#010b"))
        
def checkParity(byteArray):
    # Returns true if odd parity is correct.
    bitCount = 0
    for byte in byteArray:
        for i in range(8):
            bitCount += byte & 0x01
            byte = byte >> 1
    return bitCount % 2 == 1

def getSensorData(chk = False, needValidData = True):
    sensorDataCHK = [0x30, 0x00, 0x00, 0x02]
    sensorData = [0x30, 0x00, 0x00, 0x01]
    msg = sensorDataCHK if chk else sensorData
    spi.writebytes(msg)
    time.sleep(0.005)
    resp = spi.readbytes(4)
    # Check SQ Bits
    if (resp[0] >> 5 != 0x04):
        print("Bad Sequence Bits")
        return None
    # Check Status Bits
    status = (resp[0] >> 2) & 0x03
    if (status != 0x01 and needValidData):
        print("Bad Sensor Status: " + str(status))
        return None
    if not checkParity(resp):
        print("Bad Parity")
        printResp(resp)
        return None
    return resp

def getAngularRate(data):
    # Returns angular rate in degrees per second
    rate = data[0] & 0x03
    rate = (rate << 8) | data[1] 
    rate = (rate << 8) | data[2]
    rate = rate >> 2
    rate = ctypes.c_short(rate).value # put it in the correct box so two's complement works
    rate /= 80.0 # convert from rate data to degrees per second
    return rate
    
def startupSequence():
    resp = spi.readbytes(4)
    if (int.from_bytes(resp, byteorder="big") == 1):
        success = False
        print("Running startup sequence . . .")
        getSensorData(True, False) # Gibberish
        resp = getSensorData(needValidData=False) # FF || FE
        if resp != None and (resp[3] == 0xFF or resp[3] == 0xFE):
            success = True
        resp = getSensorData(needValidData=False) # FF || FE
        if resp != None and (resp[3] == 0xFF or resp[3] == 0xFE):
            success = True
        print("Ended startup sequence.\n")
        return success
    else:
        print("Gyro already started.")
        return True
    
angle = 0
lastTime = 0
degreeDriftDeadband = 0.02
success = startupSequence()
print("Startup sequence success? " + str(success))
if (success):
    while True:
        data = getSensorData()
        if (data != None):
            angularRate = getAngularRate(data)
            currentTime = time.time()
            if (lastTime == 0):
                lastTime = currentTime
                continue
            dt = currentTime - lastTime
            angleAdd = angularRate * dt
            if (abs(angleAdd) > degreeDriftDeadband):
                angle += angleAdd
            lastTime = currentTime
            print(str(angle) + " degrees.")
            # print(str(rate) + " degrees per second.")
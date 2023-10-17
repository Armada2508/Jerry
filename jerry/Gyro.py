import ctypes
import time
from typing import Final

import spidev  # Linux only

# https://www.analog.com/media/en/technical-documentation/data-sheets/ADXRS450.pdf
# https://web.archive.org/web/20231017193845/https://www.analog.com/media/en/technical-documentation/data-sheets/ADXRS450.pdf

class Gyro:
    # SPI
    spi = spidev.SpiDev()
    spi.open(0, 0)

    # SPI Settings
    spi.max_speed_hz = 8080000
    spi.lsbfirst = False
    spi.mode = 0b00
    
    degreeDriftDeadband: Final[float]
    angle: float = 0
    success: bool = False
    lastTime: float = 0
    
    def __init__(self, deadband):
        # automatically runs startup sequence on creation of gyro
        self.degreeDriftDeadband = deadband
        self.success = self.startupSequence()
        print("Startup sequence success? " + str(self.success))
        
    def getAngle(self) -> float:
        return self.angle
    
    def printResp(self, resp) -> None:
        for byte in resp:
            print(format(byte, "#010b"))
            
    def checkParity(self, byteArray) -> bool:
        # Returns true if odd parity is correct.
        bitCount = 0
        for byte in byteArray:
            for i in range(8):
                bitCount += byte & 0x01
                byte = byte >> 1
        return bitCount % 2 == 1

    def getSensorData(self, chk = False, needValidData = True):
        sensorDataCHK = [0x30, 0x00, 0x00, 0x02]
        sensorData = [0x30, 0x00, 0x00, 0x01]
        msg = sensorDataCHK if chk else sensorData
        self.spi.writebytes(msg)
        time.sleep(0.001)
        resp = self.spi.readbytes(4)
        # Check SQ Bits
        if (resp[0] >> 5 != 0x04):
            print("Bad Sequence Bits")
            return None
        # Check Status Bits
        status = (resp[0] >> 2) & 0x03
        if (status != 0x01 and needValidData):
            print("Bad Sensor Status: " + str(status))
            return None
        if not self.checkParity(resp):
            print("Bad Parity")
            self.printResp(resp)
            return None
        return resp

    def getAngularVelocity(self, data) -> float:
        # Returns angular velocity in degrees per second
        rate = data[0] & 0x03
        rate = (rate << 8) | data[1] 
        rate = (rate << 8) | data[2]
        rate = rate >> 2
        rate = ctypes.c_short(rate).value # put it in the correct box so two's complement works
        rate /= 80.0 # convert from rate data to degrees per second
        return rate
        
    def startupSequence(self) -> bool:
        # Returns whether it was a successful startup or not
        resp = self.spi.readbytes(4)
        if (int.from_bytes(resp, byteorder="big") == 1):
            success = 0
            print("Running startup sequence . . .")
            self.getSensorData(True, False) # Gibberish
            time.sleep(0.05)
            resp = self.getSensorData(needValidData=False) # FF || FE
            time.sleep(0.05)
            if resp != None and (resp[3] == 0xFF or resp[3] == 0xFE):
                success += 1
            resp = self.getSensorData(needValidData=False) # FF || FE
            time.sleep(0.05)
            if resp != None and (resp[3] == 0xFF or resp[3] == 0xFE):
                success += 1
            print("Ended startup sequence.\n")
            return success == 2
        else:
            print("Gyro already started.")
            return True
        
    def updateAngle(self) -> None:
        data = self.getSensorData()
        if (data != None):
            angularVelocity = self.getAngularVelocity(data)
            currentTime = time.time()
            if (self.lastTime == 0): # Skip first poll
                self.lastTime = currentTime
            dt = currentTime - self.lastTime
            angleAdd = angularVelocity * dt
            if (abs(angleAdd) > self.degreeDriftDeadband):
                self.angle += angleAdd
            self.lastTime = currentTime
            
    def updateAngleContinuously(self) -> None:
        while True:
            self.updateAngle()
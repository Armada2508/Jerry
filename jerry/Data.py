import math
import re
from typing import Final


class Constants:
    # Sockets
    rpiIP: Final[str] = "raspberrypi.local"
    listenIP: Final[str] = "0.0.0.0"
    port: Final[int] = 13505
    socketClose: Final[str] = "Socket Closed"
    enabledMsg: Final[str] = "ENABLED"
    disabledMsg: Final[str] = "DISABLED"
    clientTimeoutSec: Final[int] = 3
    # Motors
    talonSignalPins: tuple[int] = (5,)
    talonFrequencyHz: Final[int] = 100 # Talon SRX period is 10 ms
    # Misc
    clientSleepSec: Final[float] = 0.05

class JoystickData:
    
    ID: Final[int]
    axis0: Final[float]
    axis1: Final[float]
    axis2: Final[float]
    axis3: Final[float]
    button0: Final[int]
    button1: Final[int]
    button2: Final[int]
    button3: Final[int]
    button4: Final[int]
    button5: Final[int]
    button6: Final[int]
    button7: Final[int]
    button8: Final[int]
    button9: Final[int]
    button10: Final[int]
    button11: Final[int]
    
    def __init__(self, ID, axis0, axis1, axis2, axis3, button0, button1, button2, button3, button4, button5, button6, button7, button8, button9, button10, button11) -> None:
        self.ID = ID
        self.axis0 = axis0
        self.axis1 = axis1
        self.axis2 = axis2
        self.axis3 = axis3
        self.button0 = button0
        self.button1 = button1
        self.button2 = button2
        self.button3 = button3
        self.button4 = button4
        self.button5 = button5
        self.button6 = button6
        self.button7 = button7
        self.button8 = button8
        self.button9 = button9
        self.button10 = button10
        self.button11 = button11
    
    def __str__(self) -> str:
        return "Joystick: {} \nAxis: 0: {}, 1: {}, 2: {}, 3: {} \nButtons: 0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}, 8: {}, 9: {}, 10: {}, 11: {}".format(
            self.ID,
            self.axis0,
            self.axis1,
            self.axis2,
            self.axis3,
            bool(self.button0),
            bool(self.button1),
            bool(self.button2),
            bool(self.button3),
            bool(self.button4),
            bool(self.button5),
            bool(self.button6),
            bool(self.button7),
            bool(self.button8),
            bool(self.button9),
            bool(self.button10),
            bool(self.button11)
        )
        
    def __eq__(self, other):
        tolerance = 0.0001
        if self is other:
            return True
        if isinstance(other, JoystickData):
            return (
                self.ID == other.ID and
                math.isclose(self.axis0, other.axis0, rel_tol=tolerance) and
                math.isclose(self.axis1, other.axis1, rel_tol=tolerance) and
                math.isclose(self.axis2, other.axis2, rel_tol=tolerance) and
                math.isclose(self.axis3, other.axis3, rel_tol=tolerance) and
                self.button0 == other.button0 and
                self.button1 == other.button1 and
                self.button2 == other.button2 and
                self.button3 == other.button3 and
                self.button4 == other.button4 and
                self.button5 == other.button5 and
                self.button6 == other.button6 and
                self.button7 == other.button7 and
                self.button8 == other.button8 and
                self.button9 == other.button9 and
                self.button10 == other.button10 and
                self.button10 == other.button11
            )
        return False
        
    def toRaw(self) -> bytes:
        return "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
            self.ID,
            JoystickData.__roundAxis(self.axis0),
            JoystickData.__roundAxis(self.axis1),
            JoystickData.__roundAxis(self.axis2),
            JoystickData.__roundAxis(self.axis3),
            self.button0,
            self.button1,
            self.button2,
            self.button3,
            self.button4,
            self.button5,
            self.button6,
            self.button7,
            self.button8,
            self.button9,
            self.button10,
            self.button11
        ).encode("utf-8")
    
    @staticmethod    
    def __roundAxis(axis: float):
        precision = 2 + 7
        string = str(axis)
        if len(string) < precision: 
            return string[0:len(string)-1:1]
        else:
            return string[0:precision:1] 
        
    @staticmethod
    def fromRaw(rawBytes: bytes):
        data = re.split(r",", rawBytes.decode())
        return JoystickData(
            int(data[0]),
            float(data[1]),
            float(data[2]),
            float(data[3]),
            float(data[4]),
            int(data[5]),
            int(data[6]),
            int(data[7]),
            int(data[8]),
            int(data[9]),
            int(data[10]),
            int(data[11]),
            int(data[12]),
            int(data[13]),
            int(data[14]),
            int(data[15]),
            int(data[16]),
        )
        
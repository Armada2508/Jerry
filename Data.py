import re
from typing import Final


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
    
    def toRaw(self) -> bytes:
        return "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
            self.ID,
            self.axis0,
            self.axis1,
            self.axis2,
            self.axis3,
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
    def fromRaw(rawBytes: bytes):
        data = re.split(r",", rawBytes.decode())
        print(data[5])
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
        
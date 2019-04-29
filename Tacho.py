import time
import RPi.GPIO as GPIO

class Tacho:

    def __init__(self, port):
        self.port = port
        self.lastValue = 0
        self.lastChangeTime = 0     # last time the tacho changed (sec)
        self.speed = None           # cm/sec
        self.count = 0              # Number of tach changes in total
        self.cmPerSec = 1.0         # 1 tacho tick = 1 cm

    def isValid(self):
        return (self.count >= 2)

    def tick(self):
        value = GPIO.input(self.port)
        if value != self.lastValue:
            self.lastValue = value
            now = time.time()
            tickTime = now - self.lastChangeTime
            self.lastChangeTime = now
            self.count = self.count + 1
            if self.isValid():
                self.speed = self.cmPerSec / tickTime

    def asString(self):
        if self.isValid():
            return "{0:d} {1:5.2f}".format(self.count, self.speed)
        else:
            return "{0:d}     -".format(self.count)



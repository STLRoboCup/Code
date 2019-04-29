import math
from adafruit_motorkit import MotorKit
from Tacho import Tacho
from Sample import Sample

class MotorControl:
    #modes
    MANUAL = 'manual'
    DEAD_RECKONING = 'dead-reckoning'
    LINE_FOLOW = 'line-folow'

    def __init__(self, tachoGpioLeft, tachoGpioRight):
        self.mode = MotorControl.MANUAL
        self.throttleReference = 0
        self.diff = 0
        self.controlSampler = Sample(self.ctrlLoop, 0.1)  # 100 ms
        self.tachoL = Tacho(tachoGpioLeft)
        self.tachoR = Tacho(tachoGpioRight)
        self.tachoSamplerL = Sample(self.tachoL.tick, 0.02)  # 20 ms
        self.tachoSamplerR = Sample(self.tachoR.tick, 0.02)
        self.kit = MotorKit()
        # Dead reckoning
        self.throttle = (0.0, 0.0)
        self.tripStart = (0, 0)
        self.a = 0.06
        self.i = 0.11

    def stop(self):
        self.mode = MotorControl.MANUAL
        self.throttle = (0.0, 0.0)
        self.setMotor(0.0, 0.0)

    def tick(self, now):
        self.tachoSamplerL.tick(now)
        self.tachoSamplerR.tick(now)
        if(self.mode == MotorControl.DEAD_RECKONING):
            self.controlSampler.tick(now)

    def ctrlLoop(self):
        (tripL, tripR) = self.getTrip()
        tripDelta = tripL - tripR
        throttle = self.a * tripDelta + self.i
        throttleHalf = throttle / 2.0
        throttleL = self.throttleReference - throttleHalf
        throttleR = self.throttleReference + throttleHalf
        if(self.throttleReference < throttleHalf):
            throttleL = 0.0
        self.throttle = (throttleL, throttleR)
        self.setMotor(throttleL, throttleR)

    def setThrottle(self, throttle):
        self.mode = MotorControl.DEAD_RECKONING
        self.throttleReference = throttle

    def setMotor(self, throttleL, throttleR):
        # User for mode MANUAL
        # HF=motor3 VF=motor1 HB=motor2 VB=motor4.H-side er frem=positive tal, og paa V-side er de negativ
        print("Motor throttle left: %.2f right: %.2f" % (throttleL, throttleR))
        throttleL = max(-1.0, min(1.0, throttleL))
        throttleR = max(-1.0, min(1.0, throttleR))
        self.kit.motor1.throttle = -throttleL
        #self.kit.motor4.throttle = -speedL
        #self.kit.motor2.throttle = speedR
        self.kit.motor3.throttle = throttleR

    def printTacho(self):
        print('left: '+self.tachoL.asString()+ '    right: '+self.tachoR.asString())

    def resetTrip(self):
        self.tripStart = (self.tachoL.count, self.tachoR.count)

    def getTrip(self):
        tripL = self.tachoL.count - self.tripStart[0]
        tripR = self.tachoR.count - self.tripStart[1]
        return (tripL, tripR)
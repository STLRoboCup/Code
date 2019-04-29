import time
import sys
import RPi.GPIO as GPIO
from Tacho import Tacho
from Sample import Sample
from Statistics import Statistics
from MotorControl import MotorControl
from Tick import Tick

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN)     # Richt Tacho
GPIO.setup(21, GPIO.IN)     # Left Tacho


motorCtrl = MotorControl(21, 20)

speedL = 0.2
speedR = 0.2
duration = 2   # sec

if(len(sys.argv) > 3):
    speedL = float(sys.argv[1]) / 10.0
    speedR = float(sys.argv[2]) / 10.0
    duration = int(sys.argv[3])


motorCtrl.setMotor(speedL,speedR)
print("Ready. Duration: "+str(duration))

sampleTime = 0.001   # sec
tick = Tick(sampleTime)

printSampler =  Sample(motorCtrl.printTacho, 0.2)
motorCtrl.setThrottle(0.4)

samples = int(duration / sampleTime)
for n in range(samples):
    now = time.time()   # sec
    motorCtrl.tick(now)
    printSampler.tick(now)
    tick.waitForNextTick()

motorCtrl.stop()
motorCtrl.setMotor(0, 0)
print('codeRunTimeStatistics: ' + tick.codeRunTimeStatistics.asString())
print('tickTimeStatistics:    ' + tick.tickTimeStatistics.asString())
print('Sliped samples. L: '+str(motorCtrl.tachoSamplerL.slipped)+' R: '+str(motorCtrl.tachoSamplerR.slipped))
#for i in motorCtrl.tachoSamplerL.deltaList:
#    print(' delta '+str(i))



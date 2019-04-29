import time
from Statistics import Statistics

class Tick:
    
    def __init__(self, sampleTime):
        self.sampleTime = sampleTime
        self.codeStarTime = 0
        self.nextTickTime = 0
        self.codeRunTimeStatistics = Statistics()
        self.tickTimeStatistics = Statistics()


    def waitForNextTick(self):
        now1 = time.time()
        if self.codeStarTime > 0:
            codeRunTime = now1 - self.codeStarTime
            self.codeRunTimeStatistics.add(codeRunTime)
        sleepTime = (self.nextTickTime - now1)
        #print(" sleepTime: %.6f code run time: %.6f" % (sleepTime, codeRunTime))
        if(sleepTime < 0):
            self.nextTickTime = now1 + self.sampleTime
        else:
            self.nextTickTime = self.nextTickTime + self.sampleTime
            time.sleep(sleepTime)
        now2 = time.time()
        if self.codeStarTime > 0:
            tickTime = now2 - self.codeStarTime;
            self.tickTimeStatistics.add(tickTime)
        self.codeStarTime = now2

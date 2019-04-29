
import time


class Sample:

    def __init__(self, method, sampleInterval):
        """
        O Opretter et sample objekt der bruges til at kalde en metode med bestem interval.
        :param method: Metode der skal kalders
        :param sampleInterval: Sampling interval i sec.
        """
        self.method = method
        self.sampleInterval = sampleInterval
        self.nextSampleTime = 0
        self.slipped = 0
        self.deltaList = []

    def tick(self, now):   # now : aktuel tid i sec.
        if now < self.nextSampleTime:
            return
        if self.nextSampleTime == 0:
            self.nextSampleTime = now
        self.deltaList.append(now - self.nextSampleTime)
        next = self.nextSampleTime + self.sampleInterval
        while now > next:
            self.slipped = self.slipped + 1
            next = now + self.sampleInterval
        self.nextSampleTime = next
        #print('Call metod %.6f ' % now)
        self.method()

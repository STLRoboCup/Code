import math

class Statistics:

    def __init__(self):
        self.count = 0
        self.M2 = 0
        self.mean = 0
        self.min = 1000000
        self.max = -1000000


    def add(self, newValue):
        # calculatin vairans
        self.count += 1
        delta = newValue - self.mean
        self.mean += delta / self.count
        delta2 = newValue - self.mean
        self.M2 += delta * delta2
        # min / max
        self.min = min(newValue, self.min)
        self.max = max(newValue, self.max)


    def variance(self):
        if self.count < 2:
            return float('nan')
        else:
            return self.M2 / self.count


    def standardDeviation(self):
        if self.count < 2:
            return float('nan')
        else:
            return math.sqrt( self.M2 / self.count)

    def print(self, text):
        #print(text+" avg %.6f min: %.6f max: %.6f var: %.6f std.dev: %.6f" % (self.mean, self.min, self.max, self.variance(), self.standardDeviation()))
        print(text+" avg %f min: %f max: %f var: %f std.dev: %f" % (self.mean, self.min, self.max, self.variance(), self.standardDeviation()))

    def asString(self):
        text = " avg {0:f} min: {1:f} max: {2:f} var: {3:f} std.dev: {4:f} count: {5:d}"\
            .format(self.mean, self.min, self.max, self.variance(), self.standardDeviation(), self.count)
        return text

import numpy as np

class WtKlineData:
    def __init__(self, size:int):
        self.size = size
        self.count = 0

        self.bartimes = np.zeros(self.size)
        self.opens = np.zeros(self.size)
        self.highs = np.zeros(self.size)
        self.lows = np.zeros(self.size)
        self.closes = np.zeros(self.size)
        self.volumns = np.zeros(self.size)

    def append_bar(self, newBar:dict):

        pos = self.count
        if pos == self.size:
            self.bartimes[:-1] = self.bartimes[1:]
            self.opens[:-1] = self.opens[1:]
            self.highs[:-1] = self.highs[1:]
            self.lows[:-1] = self.lows[1:]
            self.closes[:-1] = self.closes[1:]
            self.volumns[:-1] = self.volumns[1:]

            pos = -1
        else:
            self.count += 1
        self.bartimes[pos] = newBar["bartime"]
        self.opens[pos] = newBar["open"]
        self.highs[pos] = newBar["high"]
        self.lows[pos] = newBar["low"]
        self.closes[pos] = newBar["close"]
        self.volumns[pos] = newBar["volumn"]

    def is_empty(self) -> bool:
        return self.count==0

    def clear(self):
        self.count = 0

        self.bartimes = np.zeros(self.size)
        self.opens = np.zeros(self.size)
        self.highs = np.zeros(self.size)
        self.lows = np.zeros(self.size)
        self.closes = np.zeros(self.size)
        self.volumns = np.zeros(self.size)

    def get_last_bar(self) -> dict:
        if self.is_empty():
            return None

        lastBar = dict()
        lastBar["bartime"] = self.bartimes[-1]
        lastBar["open"] = self.opens[-1]
        lastBar["high"] = self.highs[-1]
        lastBar["low"] = self.lows[-1]
        lastBar["close"] = self.closes[-1]
        lastBar["volumn"] = self.volumns[-1]

        return lastBar

class WtTickData:
    def __init__(self, size:int):
        self.size = size
        self.count = 0

        self.times = np.zeros(self.size)
        self.opens = np.zeros(self.size)
        self.highs = np.zeros(self.size)
        self.lows = np.zeros(self.size)
        self.prices = np.zeros(self.size)

    def append_tick(self, newTick:dict):

        pos = self.count
        if pos == self.size:
            self.times[:-1] = self.times[1:]
            self.opens[:-1] = self.opens[1:]
            self.highs[:-1] = self.highs[1:]
            self.lows[:-1] = self.lows[1:]
            self.prices[:-1] = self.prices[1:]

            pos = -1
        else:
            self.count += 1
        self.times[pos] = newTick["time"]
        self.opens[pos] = newTick["open"]
        self.highs[pos] = newTick["high"]
        self.lows[pos] = newTick["low"]
        self.prices[pos] = newTick["price"]

    def is_empty(self) -> bool:
        return self.count==0

    def clear(self):
        self.count = 0

        self.times = np.zeros(self.size)
        self.opens = np.zeros(self.size)
        self.highs = np.zeros(self.size)
        self.lows = np.zeros(self.size)
        self.prices = np.zeros(self.size)

    def get_last_tick(self) -> dict:
        if self.is_empty():
            return None

        lastTick = dict()
        lastTick["time"] = self.times[-1]
        lastTick["open"] = self.opens[-1]
        lastTick["high"] = self.highs[-1]
        lastTick["low"] = self.lows[-1]
        lastTick["price"] = self.prices[-1]
        return lastTick
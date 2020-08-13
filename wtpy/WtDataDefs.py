import numpy as np
from pandas import DataFrame

class WtKlineData:
    def __init__(self, size:int):
        self.size:int = size
        self.count:int = 0

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

        self.bartimes:np.ndarray = np.zeros(self.size)
        self.opens:np.ndarray = np.zeros(self.size)
        self.highs:np.ndarray = np.zeros(self.size)
        self.lows:np.ndarray = np.zeros(self.size)
        self.closes:np.ndarray = np.zeros(self.size)
        self.volumns:np.ndarray = np.zeros(self.size)

    def get_bar(self, iLoc:int = -1) -> dict:
        if self.is_empty():
            return None

        lastBar = dict()
        lastBar["bartime"] = self.bartimes[iLoc]
        lastBar["open"] = self.opens[iLoc]
        lastBar["high"] = self.highs[iLoc]
        lastBar["low"] = self.lows[iLoc]
        lastBar["close"] = self.closes[iLoc]
        lastBar["volumn"] = self.volumns[iLoc]

        return lastBar

    def to_df(self) -> DataFrame:
        ret = DataFrame({
            "bartime":self.bartimes,
            "open":self.opens,
            "high":self.highs,
            "low":self.lows,
            "close":self.closes,
            "volumn":self.volumns
        })
        ret.set_index(self.bartimes)
        return ret

class WtTickData:
    def __init__(self, size:int):
        self.size:int = size
        self.count:int = 0

        self.times:np.ndarray = np.zeros(self.size)
        self.opens:np.ndarray = np.zeros(self.size)
        self.highs:np.ndarray = np.zeros(self.size)
        self.lows:np.ndarray = np.zeros(self.size)
        self.prices:np.ndarray = np.zeros(self.size)

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

    def get_tick(self, iLoc:int=-1) -> dict:
        if self.is_empty():
            return None

        lastTick = dict()
        lastTick["time"] = self.times[iLoc]
        lastTick["open"] = self.opens[iLoc]
        lastTick["high"] = self.highs[iLoc]
        lastTick["low"] = self.lows[iLoc]
        lastTick["price"] = self.prices[iLoc]
        return lastTick

    def to_df(self) -> DataFrame:
        ret = DataFrame({
            "time":self.times,
            "open":self.opens,
            "high":self.highs,
            "low":self.lows,
            "price":self.prices
        })
        ret.set_index(self.times)
        return ret
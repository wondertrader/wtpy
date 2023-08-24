import numpy as np
import ctypes

NpTypeBar = np.dtype([('date','u4'),('reserve','u4'),('time','u8'),('open','d'),\
                ('high','d'),('low','d'),('close','d'),('settle','d'),\
                ('turnover','d'),('volume','d'),('open_interest','d'),('diff','d')])

class WtNpKline:
    def __init__(self, isDay:bool = False):
        self._data:np.ndarray = None
        self.isDay = isDay
        self._bartimes:np.ndarray = None

    def set_data(self, firstBar, count:int):
        c_bytes = ctypes.string_at(firstBar, count*NpTypeBar.itemsize)
        self._data = np.frombuffer(c_bytes, dtype=NpTypeBar, count=count)
        self._data.flags.writeable = False

    @property
    def ndarray(self) -> np.ndarray:
        return self._data
    
    @property
    def opens(self) -> np.ndarray:
        return self._data["open"]

    @property
    def highs(self) -> np.ndarray:
        return self._data["high"]

    @property
    def lows(self) -> np.ndarray:
        return self._data["low"]

    @property
    def closes(self) -> np.ndarray:
        return self._data["close"]

    @property
    def volumes(self) -> np.ndarray:
        return self._data["volume"]

    @property
    def bartimes(self) -> np.ndarray:
        '''
        这里应该会构造一个副本，可以暂存一个
        '''
        if self._bartimes is None:
            if self.isDay:
                self._bartimes = self._data["date"] 
            else:
                self._bartimes = self._data["time"] + 199000000000
        return self._bartimes
    
    def get_bar(self, iLoc:int = -1) -> tuple:
        return self._data[iLoc]
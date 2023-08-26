from wtpy.DequeRecord import DequeRecord
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
import numpy as np
import pandas as pd

import numpy as np
from ctypes import addressof

from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct

NpTypeBar = np.dtype([('date','u4'),('reserve','u4'),('time','u8'),('open','d'),\
                ('high','d'),('low','d'),('close','d'),('settle','d'),\
                ('turnover','d'),('volume','d'),('open_interest','d'),('diff','d')], align=True)

NpTypeTick = np.dtype([('exchg','S16'),('code','S32'),('price','d'),('open','d'),('high','d'),('low','d'),('settle_price','d'),\
                ('upper_limit','d'),('lower_limit','d'),('total_volume','d'),('volume','d'),('total_turnover','d'),('turn_over','d'),\
                ('open_interest','d'),('diff_interest','d'),('trading_date','u4'),('action_date','u4'),('action_time','u4'),\
                ('reserve','u4'),('pre_close','d'),('pre_settle','d'),('pre_interest','d'),\
                ('bid_price_0','d'),('bid_price_1','d'),('bid_price_2','d'),('bid_price_3','d'),('bid_price_4','d'),\
                ('bid_price_5','d'),('bid_price_6','d'),('bid_price_7','d'),('bid_price_8','d'),('bid_price_9','d'),\
                ('ask_price_0','d'),('ask_price_1','d'),('ask_price_2','d'),('ask_price_3','d'),('ask_price_4','d'),\
                ('ask_price_5','d'),('ask_price_6','d'),('ask_price_7','d'),('ask_price_8','d'),('ask_price_9','d'),\
                ('bid_qty_0','d'),('bid_qty_1','d'),('bid_qty_2','d'),('bid_qty_3','d'),('bid_qty_4','d'),\
                ('bid_qty_5','d'),('bid_qty_6','d'),('bid_qty_7','d'),('bid_qty_8','d'),('bid_qty_9','d'),\
                ('ask_qty_0','d'),('ask_qty_1','d'),('ask_qty_2','d'),('ask_qty_3','d'),('ask_qty_4','d'),\
                ('ask_qty_5','d'),('ask_qty_6','d'),('ask_qty_7','d'),('ask_qty_8','d'),('ask_qty_9','d')])

class WtTickRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields={
            'time': np.uint64,
            'exchg': 'U16',
            'code': 'U32',

            'price': np.double,
            'open': np.double,
            'high': np.double,
            'low': np.double,
            'settle_price': np.double,

            'upper_limit': np.double,
            'lower_limit': np.double,

            'total_volume': np.double,
            'volume': np.double,
            'total_turnover': np.double,
            'turn_over': np.double,
            'open_interest': np.double,
            'diff_interest': np.double,

            'trading_date': np.uint32,
            'action_date': np.uint32,
            'action_time': np.uint32,

            'pre_close': np.double,
            'pre_settle': np.double,
            'pre_interest': np.double,

            'bid_price_0': np.double,
            'bid_price_1': np.double,
            'bid_price_2': np.double,
            'bid_price_3': np.double,
            'bid_price_4': np.double,
            'bid_price_5': np.double,
            'bid_price_6': np.double,
            'bid_price_7': np.double,
            'bid_price_8': np.double,
            'bid_price_9': np.double,

            'ask_price_0': np.double,
            'ask_price_1': np.double,
            'ask_price_2': np.double,
            'ask_price_3': np.double,
            'ask_price_4': np.double,
            'ask_price_5': np.double,
            'ask_price_6': np.double,
            'ask_price_7': np.double,
            'ask_price_8': np.double,
            'ask_price_9': np.double,

            'bid_qty_0': np.double,
            'bid_qty_1': np.double,
            'bid_qty_2': np.double,
            'bid_qty_3': np.double,
            'bid_qty_4': np.double,
            'bid_qty_5': np.double,
            'bid_qty_6': np.double,
            'bid_qty_7': np.double,
            'bid_qty_8': np.double,
            'bid_qty_9': np.double,

            'ask_qty_0': np.double,
            'ask_qty_1': np.double,
            'ask_qty_2': np.double,
            'ask_qty_3': np.double,
            'ask_qty_4': np.double,
            'ask_qty_5': np.double,
            'ask_qty_6': np.double,
            'ask_qty_7': np.double,
            'ask_qty_8': np.double,
            'ask_qty_9': np.double
        })

    def from_struct(self, data: WTSTickStruct):
        return self.append(
            (
                np.uint64(data.action_date)*1000000000+data.action_time,
                data.exchg,
                data.code,
                data.price,
                data.open,
                data.high,
                data.low,
                data.settle_price,
                data.upper_limit,
                data.lower_limit,
                data.total_volume,
                data.volume,
                data.total_turnover,
                data.turn_over,
                data.open_interest,
                data.diff_interest,
                data.trading_date,
                data.action_date,
                data.action_time,
                data.pre_close,
                data.pre_settle,
                data.pre_interest,

                data.bid_price_0,
                data.bid_price_1,
                data.bid_price_2,
                data.bid_price_3,
                data.bid_price_4,
                data.bid_price_5,
                data.bid_price_6,
                data.bid_price_7,
                data.bid_price_8,
                data.bid_price_9,

                data.ask_price_0,
                data.ask_price_1,
                data.ask_price_2,
                data.ask_price_3,
                data.ask_price_4,
                data.ask_price_5,
                data.ask_price_6,
                data.ask_price_7,
                data.ask_price_8,
                data.ask_price_9,

                data.bid_qty_0,
                data.bid_qty_1,
                data.bid_qty_2,
                data.bid_qty_3,
                data.bid_qty_4,
                data.bid_qty_5,
                data.bid_qty_6,
                data.bid_qty_7,
                data.bid_qty_8,
                data.bid_qty_9,

                data.ask_qty_0,
                data.ask_qty_1,
                data.ask_qty_2,
                data.ask_qty_3,
                data.ask_qty_4,
                data.ask_qty_5,
                data.ask_qty_6,
                data.ask_qty_7,
                data.ask_qty_8,
                data.ask_qty_9
            )
        )

class WtOrdQueRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields={
            'time': np.uint64,
            'exchg': 'U16',
            'code': 'U32',
            
            'trading_date': np.uint32,
            'action_date': np.uint32,
            'action_time': np.uint32,

            'side': np.int32,
            'price': np.double,
            'order_items': np.uint32,
            'qsize': np.uint32,
            'volumes': np.uint32*50
        })

class WtOrdDtlRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields={
            'time': np.uint64,
            'exchg': 'U16',
            'code': 'U32',
            
            'trading_date': np.uint32,
            'action_date': np.uint32,
            'action_time': np.uint32,

            'index': np.uint32,
            'side': np.int32,
            'price': np.double,
            'volume': np.uint32,
            'otype': np.int32
        })

class WtTransRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields={
            'time': np.uint64,
            'exchg': 'U16',
            'code': 'U32',

            'trading_date': np.uint32,
            'action_date': np.uint32,
            'action_time': np.uint32,

            'index': np.uint32,
            'ttype': np.int32,
            'side': np.int32,

            'price': np.double,
            'volume': np.uint32,
            'ask_order': np.int32,
            'bid_order': np.int32
        })

class WtBarRecords(DequeRecord):
    def __init__(self, size: int):
        super().__init__(size=size, fields=dict(
            date=np.uint32,
            bartime=np.uint64,
            open=np.double,
            high=np.double,
            low=np.double,
            close=np.double,
            settle=np.double,
            money=np.double,
            volume=np.double,
            hold=np.double,
            diff=np.double,
        ))

    @property
    def opens(self) -> np.ndarray:
        return self.open

    @property
    def highs(self) -> np.ndarray:
        return self.high

    @property
    def lows(self) -> np.ndarray:
        return self.low

    @property
    def closes(self) -> np.ndarray:
        return self.close

    @property
    def volumes(self) -> np.ndarray:
        return self.volume

    @property
    def bartimes(self) -> np.ndarray:
        return self.bartime

    def get_bar(self, iLoc:int = -1) -> dict:
        return self[iLoc]

    def to_df(self) -> pd.DataFrame:
        return pd.DataFrame(self[:], index=self.bartime)

    def from_struct(self, data: WTSBarStruct) -> int:
        return self.append(
            (
                data.date,
                data.time if (data.time == data.date or data.time == 0) else data.time + 199000000000,
                data.open,
                data.high,
                data.low,
                data.close,
                data.settle,
                data.money,
                data.vol,
                data.hold,
                data.diff
            )
        )

class WtNpKline:
    def __init__(self, isDay:bool = False, forceCopy:bool = False):
        self.__data__:np.ndarray = None
        self.__isDay__:bool = isDay
        self.__force_copy__:bool = forceCopy
        self.__bartimes__:np.ndarray = None
        self.__df__:pd.DataFrame = None

    def set_data(self, firstBar, count:int):
        BarList = WTSBarStruct*count
        if self.__force_copy__:
            c_array = BarList.from_buffer_copy(BarList.from_address(addressof(firstBar.contents)))
        else:
            c_array = BarList.from_buffer(BarList.from_address(addressof(firstBar.contents)))
        self.__data__:np.ndarray = np.frombuffer(c_array, dtype=NpTypeBar, count=count)
        self.__data__.flags.writeable = self.__force_copy__

    @property
    def ndarray(self) -> np.ndarray:
        return self.__data__
    
    @property
    def opens(self) -> np.ndarray:
        return self.__data__["open"]

    @property
    def highs(self) -> np.ndarray:
        return self.__data__["high"]

    @property
    def lows(self) -> np.ndarray:
        return self.__data__["low"]

    @property
    def closes(self) -> np.ndarray:
        return self.__data__["close"]

    @property
    def volumes(self) -> np.ndarray:
        return self.__data__["volume"]

    @property
    def bartimes(self) -> np.ndarray:
        '''
        这里应该会构造一个副本，可以暂存一个
        '''
        if self.__bartimes__ is None:
            if self.__isDay__:
                self.__bartimes__ = self.__data__["date"] 
            else:
                self.__bartimes__ = self.__data__["time"] + 199000000000
        return self.__bartimes__
    
    def get_bar(self, iLoc:int = -1) -> tuple:
        return self.__data__[iLoc]
    
    @property
    def is_day(self) -> bool:
        return self.__isDay__
    
    def to_df(self) -> pd.DataFrame:
        if self.__df__ is None:
            self.__df__ = pd.DataFrame(self.__data__, index=self.bartimes)
            self.__df__.drop(columns=["date", "time", "reserve"], inplace=True)
            self.__df__["bartime"] = self.__df__.index
        return self.__df__
    
class WtNpTicks:
    def __init__(self, forceCopy:bool = False):
        self.__data__:np.ndarray = None
        self.__times__:np.ndarray = None
        self.__force_copy__:bool = forceCopy

    def set_data(self, firstTick, count:int):
        BarList = WTSTickStruct*count
        if self.__force_copy__:
            c_array = BarList.from_buffer_copy(BarList.from_address(addressof(firstTick.contents)))
        else:
            c_array = BarList.from_buffer(BarList.from_address(addressof(firstTick.contents)))
        self.__data__ = np.frombuffer(c_array, dtype=NpTypeTick, count=count)
        self.__data__.flags.writeable = False

    @property
    def ndarray(self) -> np.ndarray:
        return self.__data__
    
    @property
    def times(self) -> np.ndarray:
        if self.__times__ is None:
            self.__times__ = self.__data__["action_date"] * 1000000000 + self.__data__["action_time"]

        return self.__times__
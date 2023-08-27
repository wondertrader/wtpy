from wtpy.WtCoreDefs import WTSBarStruct, WTSOrdDtlStruct, WTSOrdQueStruct, WTSTickStruct, WTSTransStruct
import numpy as np
import pandas as pd

import numpy as np
from ctypes import POINTER, addressof

from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct

NpTypeBar = np.dtype([('date','u4'),('reserve','u4'),('time','u8'),('open','d'),\
                ('high','d'),('low','d'),('close','d'),('settle','d'),\
                ('turnover','d'),('volume','d'),('open_interest','d'),('diff','d')])

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

NpTypeTrans = np.dtype([('exchg','S16'),('code','S32'),('trading_date','u4'),('action_date','u4'),('action_time','u4'),\
                ('index','i8'),('ttype','i4'),('side','i4'),('price','d'),('volume','u4'),('askorder', np.int64),('bidorder', np.int64)])

NpTypeOrdQue = np.dtype([('exchg','S16'),('code','S32'),('trading_date','u4'),('action_date','u4'),('action_time','u4'),\
                ('side','u4'),('price','d'),('order_items','u4'),('qsize', np.int64),('volumes', np.uint32, 50)])

NpTypeOrdDtl = np.dtype([('exchg','S16'),('code','S32'),('trading_date','u4'),('action_date','u4'),('action_time','u4'),\
                ('index','i8'),('price','d'),('volume','u4'),('side','u4'),('otype','u4')])

class WtNpKline:
    '''
    基于numpy.ndarray的K线数据容器
    提供一些常用的属性和方法
    '''
    __type__:np.dtype = NpTypeBar
    def __init__(self, isDay:bool = False, forceCopy:bool = False):
        '''
        基于numpy.ndarray的K线数据容器
        @isDay      是否是日线数据, 主要用于控制bartimes的生成机制
        @forceCopy  是否强制拷贝, 如果为True, 则会拷贝一份数据, 否则会直接引用内存中的数据
                    强制拷贝主要用于WtDtHelper的read_dsb_bars和read_dmb_bars接口, 因为这两个接口返回的数据是临时的, 调用结束就会释放
        '''
        self.__data__:np.ndarray = None
        self.__isDay__:bool = isDay
        self.__force_copy__:bool = forceCopy
        self.__bartimes__:np.ndarray = None
        self.__df__:pd.DataFrame = None

    def __len__(self):
        if self.__data__ is None:
            return 0
        
        return len(self.__data__)
    
    def __getitem__(self, index:int):
        if self.__data__ is None:
            raise IndexError("No data in WtNpKline")
        
        return self.__data__[index]

    def set_day_flag(self, isDay:bool):
        if self.__isDay__ != isDay:
            self.__isDay__ = isDay
            self.__bartimes__ = None
            self.__df__ = None

    def set_data(self, firstBar, count:int):
        BarList = WTSBarStruct*count
        if self.__force_copy__:
            c_array = BarList.from_buffer_copy(BarList.from_address(addressof(firstBar.contents)))
        else:
            c_array = BarList.from_buffer(BarList.from_address(addressof(firstBar.contents)))
        npAy = np.frombuffer(c_array, dtype=self.__type__, count=count)

        # 这里有点不高效，需要拼接的地方，主要是WtDtServo的场景，这里慢点没关系
        if self.__data__ is not None:
            self.__data__ = np.concatenate((self.__data__, npAy))
            self.__data__.flags.writeable = self.__force_copy__
        else:
            self.__data__ = npAy
            self.__data__.flags.writeable = False

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
        这里应该会构造一个副本, 可以暂存一个
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
    '''
    基于numpy.ndarray的tick数据容器
    提供一些常用的属性和方法
    '''
    __type__:np.dtype = NpTypeTick
    def __init__(self, forceCopy:bool = False):
        '''
        基于numpy.ndarray的tick数据容器
        @forceCopy  是否强制拷贝, 如果为True, 则会拷贝一份数据, 否则会直接引用内存中的数据
                    强制拷贝主要用于WtDtHelper的read_dsb_ticks和read_dmb_ticks接口, 因为这两个接口返回的数据是临时的, 调用结束就会释放
        '''
        self.__data__:np.ndarray = None
        self.__times__:np.ndarray = None
        self.__force_copy__:bool = forceCopy
        self.__df__:pd.DataFrame = None

    def __len__(self):
        if self.__data__ is None:
            return 0
        
        return len(self.__data__)
    
    def __getitem__(self, index:int):
        if self.__data__ is None:
            raise IndexError("No data in WtNpTicks")
        
        return self.__data__[index]

    def set_data(self, firstTick, count:int):
        BarList = WTSTickStruct*count
        if self.__force_copy__:
            c_array = BarList.from_buffer_copy(BarList.from_address(addressof(firstTick.contents)))
        else:
            c_array = BarList.from_buffer(BarList.from_address(addressof(firstTick.contents)))

        npAy = np.frombuffer(c_array, dtype=self.__type__, count=count)
        # 这里有点不高效，需要拼接的地方主要是WtDtServo的场景，这里慢点没关系
        # 一旦触发拼接逻辑，都会拷贝一次
        if self.__data__ is not None:
            self.__data__ = np.concatenate((self.__data__, npAy))
            self.__data__.flags.writeable = self.__force_copy__
        else:
            self.__data__ = npAy
            self.__data__.flags.writeable = False

    @property
    def times(self) -> np.ndarray:
        '''
        这里应该会构造一个副本, 可以暂存一个
        '''
        if self.__times__ is None:
            self.__times__ = np.uint64(self.__data__["action_date"])*1000000000 + self.__data__["action_time"]
        return self.__times__


    def to_df(self) -> pd.DataFrame:
        if self.__df__ is None:
            self.__df__ = pd.DataFrame(self.__data__, index=self.times)
            self.__df__.drop(columns=["reserve"], inplace=True)
            self.__df__["time"] = self.__df__.index
        return self.__df__

    @property
    def ndarray(self) -> np.ndarray:
        return self.__data__
    
class WtNpTransactions:
    '''
    基于numpy.ndarray的逐笔成交数据容器
    提供一些常用的属性和方法
    '''
    __type__:np.dtype = NpTypeTrans
    def __init__(self, forceCopy:bool = False):
        '''
        基于numpy.ndarray的逐笔成交数据容器
        @forceCopy  是否强制拷贝, 如果为True, 则会拷贝一份数据, 否则会直接引用内存中的数据
                    强制拷贝主要用于WtDtHelper的read_dsb_trans和read_dmb_trans接口, 因为这两个接口返回的数据是临时的, 调用结束就会释放
        '''
        self.__data__:np.ndarray = None
        self.__force_copy__:bool = forceCopy

    def __len__(self):
        if self.__data__ is None:
            return 0
        
        return len(self.__data__)
    
    def __getitem__(self, index:int):
        if self.__data__ is None:
            raise IndexError("No data in WtNpTransactions")
        
        return self.__data__[index]

    def set_data(self, firstItem, count:int):
        DataList = WTSTransStruct*count
        if self.__force_copy__:
            c_array = DataList.from_buffer_copy(DataList.from_address(addressof(firstItem.contents)))
        else:
            c_array = DataList.from_buffer(DataList.from_address(addressof(firstItem.contents)))
        
        npAy = np.frombuffer(c_array, dtype=self.__type__, count=count)
        # 这里有点不高效，需要拼接的地方主要是WtDtServo的场景，这里慢点没关系
        # 一旦触发拼接逻辑，都会拷贝一次
        if self.__data__ is not None:
            self.__data__ = np.concatenate((self.__data__, npAy))
            self.__data__.flags.writeable = self.__force_copy__
        else:
            self.__data__ = npAy
            self.__data__.flags.writeable = False

    @property
    def ndarray(self) -> np.ndarray:
        return self.__data__
    
class WtNpOrdDetails:
    '''
    基于numpy.ndarray的逐笔委托数据容器
    提供一些常用的属性和方法
    '''
    __type__:np.dtype = NpTypeOrdDtl
    def __init__(self, forceCopy:bool = False):
        '''
        基于numpy.ndarray的逐笔委托数据容器
        @forceCopy  是否强制拷贝, 如果为True, 则会拷贝一份数据, 否则会直接引用内存中的数据
                    强制拷贝主要用于WtDtHelper的read_dsb_trans和read_dmb_trans接口, 因为这两个接口返回的数据是临时的, 调用结束就会释放
        '''
        self.__data__:np.ndarray = None
        self.__force_copy__:bool = forceCopy

    def __len__(self):
        if self.__data__ is None:
            return 0
        
        return len(self.__data__)
    
    def __getitem__(self, index:int):
        if self.__data__ is None:
            raise IndexError("No data in WtNpOrdDetails")
        
        return self.__data__[index]

    def set_data(self, firstItem, count:int):
        DataList = WTSOrdDtlStruct*count
        if self.__force_copy__:
            c_array = DataList.from_buffer_copy(DataList.from_address(addressof(firstItem.contents)))
        else:
            c_array = DataList.from_buffer(DataList.from_address(addressof(firstItem.contents)))

        npAy = np.frombuffer(c_array, dtype=self.__type__, count=count)
        # 这里有点不高效，需要拼接的地方主要是WtDtServo的场景，这里慢点没关系
        # 一旦触发拼接逻辑，都会拷贝一次
        if self.__data__ is not None:
            self.__data__ = np.concatenate((self.__data__, npAy))
            self.__data__.flags.writeable = self.__force_copy__
        else:
            self.__data__ = npAy
            self.__data__.flags.writeable = False

    @property
    def ndarray(self) -> np.ndarray:
        return self.__data__
    
class WtNpOrdQueues:
    '''
    基于numpy.ndarray的委托队列数据容器
    提供一些常用的属性和方法
    '''
    __type__:np.dtype = NpTypeOrdQue
    def __init__(self, forceCopy:bool = False):
        '''
        基于numpy.ndarray的委托队列数据容器
        @forceCopy  是否强制拷贝, 如果为True, 则会拷贝一份数据, 否则会直接引用内存中的数据
                    强制拷贝主要用于WtDtHelper的read_dsb_trans和read_dmb_trans接口, 因为这两个接口返回的数据是临时的, 调用结束就会释放
        '''
        self.__data__:np.ndarray = None
        self.__force_copy__:bool = forceCopy

    def __len__(self):
        if self.__data__ is None:
            return 0
        
        return len(self.__data__)
    
    def __getitem__(self, index:int):
        if self.__data__ is None:
            raise IndexError("No data in WtNpOrdQueues")
        
        return self.__data__[index]

    def set_data(self, firstItem, count:int):
        DataList = WTSOrdQueStruct*count
        if self.__force_copy__:
            c_array = DataList.from_buffer_copy(DataList.from_address(addressof(firstItem.contents)))
        else:
            c_array = DataList.from_buffer(DataList.from_address(addressof(firstItem.contents)))

        npAy = np.frombuffer(c_array, dtype=self.__type__, count=count)
        # 这里有点不高效，需要拼接的地方主要是WtDtServo的场景，这里慢点没关系
        # 一旦触发拼接逻辑，都会拷贝一次
        if self.__data__ is not None:
            self.__data__ = np.concatenate((self.__data__, npAy))
            self.__data__.flags.writeable = self.__force_copy__
        else:
            self.__data__ = npAy
            self.__data__.flags.writeable = False

    @property
    def ndarray(self) -> np.ndarray:
        return self.__data__
    
class WtBarCache:
    def __init__(self, isDay:bool = False, forceCopy:bool = False):
        self.records:WtNpKline = None
        self.__is_day__ = isDay
        self.__force_copy__ = forceCopy
        self.__total_count__ = 0

    def on_read_bar(self, firstItem:POINTER(WTSBarStruct), count:int, isLast:bool):
        if self.records is None:
            self.records = WtNpKline(isDay=self.__is_day__, forceCopy=self.__force_copy__)

        # 多次set_data，会在内部自动concatenate
        self.records.set_data(firstItem, count)

    def on_data_count(self, count:int):
        # 其实这里最好的处理方式是能够直接将底层的内存块拷贝，拼接成一块大的内存块
        # 但是暂时没想好怎么处理，所以只能多次set_data了，会损失一些性能，但是比以前快
        self.__total_count__ = count
        pass

class WtTickCache:
    def __init__(self, forceCopy:bool = False):
        self.records:WtNpTicks = None
        self.__force_copy__ = forceCopy
        self.__total_count__ = 0

    def on_read_tick(self, firstItem:POINTER(WTSTickStruct), count:int, isLast:bool):
        if self.records is None:
            self.records = WtNpTicks(forceCopy=self.__force_copy__)

        # 多次set_data，会在内部自动concatenate
        self.records.set_data(firstItem, count)

    def on_data_count(self, count:int):
        # 其实这里最好的处理方式是能够直接将底层的内存块拷贝，拼接成一块大的内存块
        # 但是暂时没想好怎么处理，所以只能多次set_data了，会损失一些性能，但是比以前快
        self.__total_count__ = count
        pass
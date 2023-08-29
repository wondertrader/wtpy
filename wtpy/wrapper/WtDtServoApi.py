from ctypes import cdll, CFUNCTYPE, c_char_p, c_void_p, c_bool, POINTER, c_uint64, c_uint32
from wtpy.WtCoreDefs import WTSBarStruct, WTSTickStruct
from wtpy.WtDataDefs import WtNpKline, WtNpTicks, WtBarCache, WtTickCache
from wtpy.wrapper.PlatformHelper import PlatformHelper as ph
from wtpy.WtUtilDefs import singleton
import os

CB_GET_BAR = CFUNCTYPE(c_void_p,  POINTER(WTSBarStruct), c_uint32, c_bool)
CB_GET_TICK = CFUNCTYPE(c_void_p,  POINTER(WTSTickStruct), c_uint32, c_bool)
CB_DATA_COUNT = CFUNCTYPE(c_void_p,  c_uint32)

@singleton
class WtDtServoApi:
    '''
    Wt平台数据组件C接口底层对接模块
    '''

    # api可以作为公共变量
    api = None
    ver = "Unknown"

    # 构造函数, 传入动态库名
    def __init__(self):
        paths = os.path.split(__file__)
        dllname = ph.getModule("WtDtServo")
        a = (paths[:-1] + (dllname,))
        _path = os.path.join(*a)
        self.api = cdll.LoadLibrary(_path)

        self.api.get_version.restype = c_char_p
        self.ver = bytes.decode(self.api.get_version())

        self.api.get_bars_by_range.argtypes = [c_char_p, c_char_p, c_uint64, c_uint64, CB_GET_BAR, CB_DATA_COUNT]
        self.api.get_ticks_by_range.argtypes = [c_char_p, c_uint64, c_uint64, CB_GET_TICK, CB_DATA_COUNT]

        self.api.get_bars_by_count.argtypes = [c_char_p, c_char_p, c_uint32, c_uint64, CB_GET_BAR, CB_DATA_COUNT]
        self.api.get_ticks_by_count.argtypes = [c_char_p, c_uint32, c_uint64, CB_GET_TICK, CB_DATA_COUNT]

        self.api.get_ticks_by_date.argtypes = [c_char_p, c_uint32, CB_GET_TICK, CB_DATA_COUNT]
        self.api.get_sbars_by_date.argtypes = [c_char_p, c_uint32, c_uint32, CB_GET_BAR, CB_DATA_COUNT]
        self.api.get_bars_by_date.argtypes = [c_char_p, c_char_p, c_uint32, CB_GET_BAR, CB_DATA_COUNT]

    def initialize(self, cfgfile:str, isFile:bool, logcfg:str = 'logcfg.yaml'):
        self.api.initialize(bytes(cfgfile, encoding = "utf8"), isFile, bytes(logcfg, encoding = "utf8"))

    def clear_cache(self):
        self.api.clear_cache()

    def get_bars(self, stdCode:str, period:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtNpKline:
        '''
        获取K线数据
        @stdCode    标准合约代码
        @period     基础K线周期, m1/m5/d
        @fromTime   开始时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM
        @endTime    结束时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM, 为0则读取到最后一条
        '''        
        bar_cache = WtBarCache()
        if fromTime is not None:
            ret = self.api.get_bars_by_range(bytes(stdCode, encoding="utf8"), bytes(period,'utf8'), fromTime, endTime, CB_GET_BAR(bar_cache.on_read_bar), CB_DATA_COUNT(bar_cache.on_data_count))
        else:
            ret = self.api.get_bars_by_count(bytes(stdCode, encoding="utf8"), bytes(period,'utf8'), dataCount, endTime, CB_GET_BAR(bar_cache.on_read_bar), CB_DATA_COUNT(bar_cache.on_data_count))

        if ret == 0:
            return None
        else:
            return bar_cache.records

    def get_ticks(self, stdCode:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtNpTicks:
        '''
        获取tick数据
        @stdCode    标准合约代码
        @fromTime   开始时间, 格式为yyyymmddHHMM
        @endTime    结束时间, 格式为yyyymmddHHMM, 为0则读取到最后一条
        '''        
        tick_cache = WtTickCache()
        if fromTime is not None:
            ret = self.api.get_ticks_by_range(bytes(stdCode, encoding="utf8"), fromTime, endTime, CB_GET_TICK(tick_cache.on_read_tick), CB_DATA_COUNT(tick_cache.on_data_count))
        else:
            ret = self.api.get_ticks_by_count(bytes(stdCode, encoding="utf8"), dataCount, endTime, CB_GET_TICK(tick_cache.on_read_tick), CB_DATA_COUNT(tick_cache.on_data_count))

        if ret == 0:
            return None
        else:
            return tick_cache.records

    def get_ticks_by_date(self, stdCode:str, iDate:int) -> WtNpTicks:
        '''
        按天读取tick数据
        @stdCode    标准合约代码
        @iDate      数据日期, 格式为yyyymmdd
        '''        
        tick_cache = WtTickCache()
        ret = self.api.get_ticks_by_date(bytes(stdCode, encoding="utf8"), iDate, CB_GET_TICK(tick_cache.on_read_tick), CB_DATA_COUNT(tick_cache.on_data_count))   

        if ret == 0:
            return None
        else:
            return tick_cache.records

    def get_sbars_by_date(self, stdCode:str, iSec:int, iDate:int) -> WtNpKline:
        '''
        按天读取秒线
        @stdCode    标准合约代码
        @iSec       周期, 单位s
        @iDate      数据日期, 格式为yyyymmdd
        '''        
        bar_cache = WtBarCache()
        ret = self.api.get_sbars_by_date(bytes(stdCode, encoding="utf8"), iSec, iDate, CB_GET_BAR(bar_cache.on_read_bar), CB_DATA_COUNT(bar_cache.on_data_count))

        if ret == 0:
            return None
        else:
            return bar_cache.records

    def get_bars_by_date(self, stdCode:str, period:str, iDate:int) -> WtNpKline:
        '''
        按天读取分钟线
        @stdCode    标准合约代码
        @period     周期, 分钟线
        @iDate      数据日期, 格式为yyyymmdd
        '''
        if period[0] != 'm':
            return None

        bar_cache = WtBarCache()
        ret = self.api.get_bars_by_date(bytes(stdCode, encoding="utf8"), bytes(period, encoding="utf8"), iDate, CB_GET_BAR(bar_cache.on_read_bar), CB_DATA_COUNT(bar_cache.on_data_count))

        if ret == 0:
            return None
        else:
            return bar_cache.records
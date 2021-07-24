from ctypes import cdll, CFUNCTYPE, c_char_p, c_void_p, c_bool, POINTER, c_uint64, c_uint32
from wtpy.WtCoreDefs import BarList, TickList, WTSBarStruct, WTSTickStruct
from wtpy.wrapper.PlatformHelper import PlatformHelper as ph
from wtpy.WtUtilDefs import singleton

import os
import json

CB_GET_BAR = CFUNCTYPE(c_void_p,  POINTER(WTSBarStruct), c_bool)
CB_GET_TICK = CFUNCTYPE(c_void_p,  POINTER(WTSTickStruct), c_bool)

@singleton
class WtDtServo:
    '''
    Wt平台数据组件C接口底层对接模块
    '''

    # api可以作为公共变量
    api = None
    ver = "Unknown"

    # 构造函数，传入动态库名
    def __init__(self):
        self.__config__ = dict()
        self.__cfg_commited__ = False
        paths = os.path.split(__file__)
        if ph.isWindows():  # windows平台
            if ph.isPythonX64():
                dllname = "x64/WtDtServo.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
            else:
                dllname = "x86/WtDtServo.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
        else:  # Linux平台
            dllname = "linux/libWtDtServo.so"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            self.api = cdll.LoadLibrary(_path)
        self.api.get_version.restype = c_char_p
        self.ver = bytes.decode(self.api.get_version())

        self.api.get_bars_by_range.argtypes = [c_char_p, c_char_p, c_uint64, c_uint64, CB_GET_BAR]
        self.api.get_ticks_by_range.argtypes = [c_char_p, c_uint64, c_uint64, CB_GET_TICK]

        self.api.get_bars_by_count.argtypes = [c_char_p, c_char_p, c_uint32, c_uint64, CB_GET_BAR]
        self.api.get_ticks_by_count.argtypes = [c_char_p, c_uint32, c_uint64, CB_GET_TICK]

    def __check_config__(self):
        '''
        检查设置项\n
        主要会补充一些默认设置项
        '''
        if "basefiles" not in self.__config__:
            self.__config__["basefiles"] = dict()

        if "data" not in self.__config__:
            self.__config__["data"] = {
                "store":{
                    "path":"./storage/"
                }
            }

    def setBasefiles(self, commfile:str="./common/commodities.json", contractfile:str="./common/contracts.json", 
                holidayfile:str="./common/holidays.json", sessionfile:str="./common/sessions.json", hotfile:str="./common/hots.json"):
        '''
        C接口初始化
        '''
        self.__check_config__()

        self.__config__["basefiles"]["commodity"] = commfile
        self.__config__["basefiles"]["contract"] = contractfile
        self.__config__["basefiles"]["holiday"] = holidayfile
        self.__config__["basefiles"]["session"] = sessionfile
        self.__config__["basefiles"]["hot"] = hotfile

    def setStorage(self, path:str = "./storage/"):
        self.__config__["data"]["store"]["path"] = path
    
    def commitConfig(self):
        if self.__cfg_commited__:
            return

        cfgfile = json.dumps(self.__config__, indent=4, sort_keys=True)
        try:
            self.api.initialize(bytes(cfgfile, encoding = "utf8"), False)
            self.__cfg_commited__ = True
        except OSError as oe:
            print(oe)

    def get_bars(self, stdCode:str, period:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> BarList:
        '''
        重采样K线\n
        @stdCode    标准合约代码\n
        @period     基础K线周期，m1/m5/d\n
        @fromTime   开始时间，日线数据格式yyyymmdd，分钟线数据为格式为yyyymmddHHMM\n
        @endTime    结束时间，日线数据格式yyyymmdd，分钟线数据为格式为yyyymmddHHMM，为0则读取到最后一条
        '''
        self.commitConfig()

        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        bar_cache = BarList()
        if fromTime is not None:
            ret = self.api.get_bars_by_range(bytes(stdCode, encoding="utf8"), bytes(period,'utf8'), fromTime, endTime, CB_GET_BAR(bar_cache.on_read_bar))
        else:
            ret = self.api.get_bars_by_count(bytes(stdCode, encoding="utf8"), bytes(period,'utf8'), dataCount, endTime, CB_GET_BAR(bar_cache.on_read_bar))

        if ret == 0:
            return None
        else:
            return bar_cache

    def get_ticks(self, stdCode:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> TickList:
        '''
        重采样K线\n
        @stdCode    标准合约代码\n
        @fromTime   开始时间，格式为yyyymmddHHMM\n
        @endTime    结束时间，格式为yyyymmddHHMM，为0则读取到最后一条
        '''
        self.commitConfig()

        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        tick_cache = TickList()
        if fromTime is not None:
            ret = self.api.get_ticks_by_range(bytes(stdCode, encoding="utf8"), fromTime, endTime, CB_GET_TICK(tick_cache.on_read_tick))
        else:
            ret = self.api.get_ticks_by_count(bytes(stdCode, encoding="utf8"), dataCount, endTime, CB_GET_TICK(tick_cache.on_read_tick))

        if ret == 0:
            return None
        else:
            return tick_cache
from ctypes import cdll, CFUNCTYPE, c_char_p, c_void_p, c_bool, POINTER, c_uint64
from wtpy.WtCoreDefs import BarList, TickList, WTSBarStruct, WTSTickStruct
from wtpy.wrapper.PlatformHelper import PlatformHelper as ph
import os

CB_GET_BAR = CFUNCTYPE(c_void_p,  POINTER(WTSBarStruct), c_bool)
CB_GET_TICK = CFUNCTYPE(c_void_p,  POINTER(WTSTickStruct), c_bool)

class WtDtServo:
    '''
    Wt平台数据组件C接口底层对接模块
    '''

    # api可以作为公共变量
    api = None
    ver = "Unknown"

    # 构造函数，传入动态库名
    def __init__(self):
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

        self.api.get_bars.argtypes = [c_char_p, c_char_p, c_uint64, c_uint64, CB_GET_BAR]
        self.api.get_ticks.argtypes = [c_char_p, c_uint64, c_uint64, CB_GET_TICK]

    def initialize(self, cfgfile:str = "dtservo.json", logprofile:str = "logcfg.json"):
        '''
        C接口初始化
        '''
        try:
            self.api.initialize(bytes(cfgfile, encoding = "utf8"), bytes(logprofile, encoding = "utf8"))
        except OSError as oe:
            print(oe)

    def get_bars(self, stdCode:str, period:str, fromTime:int, endTime:int) -> BarList:
        '''
        重采样K线\n
        @stdCode    标准合约代码
        @period     基础K线周期，m1/m5/d\n
        @fromTime   开始时间，日线数据格式yyyymmdd，分钟线数据为格式为yyyymmddHHMM\n
        @endTime    结束时间，日线数据格式yyyymmdd，分钟线数据为格式为yyyymmddHHMM\n
        '''
        bar_cache = BarList()
        if 0 == self.api.get_bars(bytes(stdCode, encoding="utf8"), bytes(period,'utf8'), fromTime, endTime, CB_GET_BAR(bar_cache.on_read_bar)):
            return None
        else:
            return bar_cache

    def get_ticks(self, stdCode:str, fromTime:int, endTime:int) -> TickList:
        '''
        重采样K线\n
        @stdCode    标准合约代码
        @fromTime   开始时间，格式为yyyymmddHHMMSSsss\n
        @endTime    结束时间，格式为yyyymmddHHMMSSsss\n
        '''
        tick_cache = TickList()
        if 0 == self.api.get_ticks(bytes(stdCode, encoding="utf8"), fromTime, endTime, CB_GET_TICK(TickList.on_read_tick)):
            return None
        else:
            return tick_cache
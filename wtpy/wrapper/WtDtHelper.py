from ctypes import cdll, CFUNCTYPE, c_char_p, c_void_p, c_bool, POINTER, c_int
from wtpy.WtCoreDefs import WTSTickStruct, WTSBarStruct
from wtpy.wrapper.PlatformHelper import PlatformHelper as ph
from copy import copy
import os

CB_DTHELPER_LOG = CFUNCTYPE(c_void_p,  c_char_p)
CB_DTHELPER_TICK = CFUNCTYPE(c_void_p,  POINTER(WTSTickStruct), c_bool)
CB_DTHELPER_BAR = CFUNCTYPE(c_void_p,  POINTER(WTSBarStruct), c_bool)

CB_DTHELPER_BAR_GETTER = CFUNCTYPE(c_bool, POINTER(WTSBarStruct), c_int)
CB_DTHELPER_TICK_GETTER = CFUNCTYPE(c_bool, POINTER(WTSTickStruct), c_int)

def on_log_output(message:str):
    message = bytes.decode(message, 'gbk')
    print(message)

class TickList(list):
    def on_read_tick(self, curTick:POINTER(WTSTickStruct), isLast:bool):
        self.append(copy(curTick.contents))

class BarList(list):
    def on_read_bar(self, curBar:POINTER(WTSBarStruct), isLast:bool):
        self.append(copy(curBar.contents))

cb_dthelper_log = CB_DTHELPER_LOG(on_log_output)

class WtDataHelper:
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
                dllname = "x64/WtDtHelper.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
            else:
                dllname = "x86/WtDtHelper.dll"
                a = (paths[:-1] + (dllname,))
                _path = os.path.join(*a)
                self.api = cdll.LoadLibrary(_path)
        else:  # Linux平台
            dllname = "linux/libWtDtHelper.so"
            a = (paths[:-1] + (dllname,))
            _path = os.path.join(*a)
            self.api = cdll.LoadLibrary(_path)

    def dump_bars(self, binFolder:str, csvFolder:str, strFilter:str=""):
        '''
        将目录下的.dsb格式的历史K线数据导出为.csv格式\n
        @binFolder  .dsb文件存储目录\n
        @csvFolder  .csv文件的输出目录\n
        @strFilter  代码过滤器(暂未启用)
        '''
        self.api.dump_bars(bytes(binFolder, encoding="utf8"), bytes(csvFolder, encoding="utf8"), bytes(strFilter, encoding="utf8"), cb_dthelper_log)

    def dump_ticks(self, binFolder: str, csvFolder: str, strFilter: str=""):
        '''
        将目录下的.dsb格式的历史Tik数据导出为.csv格式\n
        @binFolder  .dsb文件存储目录\n
        @csvFolder  .csv文件的输出目录\n
        @strFilter  代码过滤器(暂未启用)
        '''
        self.api.dump_ticks(bytes(binFolder, encoding="utf8"), bytes(csvFolder, encoding="utf8"), bytes(strFilter, encoding="utf8"), cb_dthelper_log)

    def trans_csv_bars(self, csvFolder: str, binFolder: str, period: str):
        '''
        将目录下的.csv格式的历史K线数据转成.dsb格式\n
        @csvFolder  .csv文件的输出目录\n
        @binFolder  .dsb文件存储目录\n
        @period     K线周期，m1-1分钟线，m5-5分钟线，d-日线
        '''
        self.api.trans_csv_bars(bytes(csvFolder, encoding="utf8"), bytes(binFolder, encoding="utf8"), bytes(period, encoding="utf8"), cb_dthelper_log)

    def read_dsb_ticks(self, tickFile: str) -> list:
        '''
        读取.dsb格式的tick数据\n
        @tickFile   .dsb的tick数据文件\n
        @return     WTSTickStruct的list
        '''
        tick_cache = TickList()
        if 0 == self.api.read_dsb_ticks(bytes(tickFile, encoding="utf8"), CB_DTHELPER_TICK(tick_cache.on_read_tick), cb_dthelper_log):
            return None
        else:
            return tick_cache

    def read_dsb_bars(self, barFile: str) -> list:
        '''
        读取.dsb格式的K线数据\n
        @tickFile   .dsb的K线数据文件\n
        @return     WTSBarStruct的list
        '''
        bar_cache = BarList()
        if 0 == self.api.read_dsb_bars(bytes(barFile, encoding="utf8"), CB_DTHELPER_BAR(bar_cache.on_read_bar), cb_dthelper_log):
            return None
        else:
            return bar_cache

    def trans_bars(self, barFile:str, getter, count:int, period:str) -> bool:
        '''
        将K线转储到dsb文件中\n
        @barFile    要存储的文件路径\n
        @getter     获取bar的回调函数\n
        @count      一共要写入的数据条数\n
        @period     周期，m1/m5/d
        '''
        cb = CB_DTHELPER_BAR_GETTER(getter)
        return self.api.trans_bars(bytes(barFile, encoding="utf8"), cb, count, bytes(period, encoding="utf8"), cb_dthelper_log)

    def trans_ticks(self, tickFile:str, getter, count:int) -> bool:
        '''
        将Tick数据转储到dsb文件中\n
        @tickFile   要存储的文件路径\n
        @getter     获取tick的回调函数\n
        @count      一共要写入的数据条数
        '''
        cb = CB_DTHELPER_TICK_GETTER(getter)
        return self.api.trans_ticks(bytes(tickFile, encoding="utf8"), cb, count, cb_dthelper_log)
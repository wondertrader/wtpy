from ctypes import cdll, CFUNCTYPE, c_char_p, c_void_p, c_bool, POINTER
from wtpy.WtCoreDefs import WTSTickStruct, WTSBarStruct
from .PlatformHelper import PlatformHelper as ph
import os
import copy

CB_DTHELPER_LOG = CFUNCTYPE(c_void_p,  c_char_p)
CB_DTHELPER_TICK = CFUNCTYPE(c_void_p,  POINTER(WTSTickStruct), c_bool)
CB_DTHELPER_BAR = CFUNCTYPE(c_void_p,  POINTER(WTSBarStruct), c_bool)

def on_log_output(message:str):
    message = bytes.decode(message, "gbk")
    print(message)

tick_cache = list()
def on_read_tick(curTick:POINTER(WTSTickStruct), isLast:bool):
    global tick_cache
    
    realTick = None
    if curTick:
        realTick = curTick.contents

    if realTick is None:
        return
    
    tick_cache.append(copy.copy(realTick))

bar_cache = list()
def on_read_bar(curBar:POINTER(WTSBarStruct), isLast:bool):
    global bar_cache
    
    realBar = None
    if curBar:
        realBar = curBar.contents

    if realBar is None:
        return
    
    bar_cache.append(copy.copy(realBar))

cb_dthelper_log = CB_DTHELPER_LOG(on_log_output)
cb_read_tick = CB_DTHELPER_TICK(on_read_tick)
cb_read_bar = CB_DTHELPER_BAR(on_read_bar)

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
        global tick_cache
        tick_cache = list()
        cnt = self.api.read_dsb_ticks(bytes(tickFile, encoding="utf8"), cb_read_tick, cb_dthelper_log)
        if cnt == 0:
            return None
        else:
            return tick_cache

    def read_dsb_bars(self, barFile: str) -> list:
        '''
        读取.dsb格式的K线数据\n
        @tickFile   .dsb的K线数据文件\n
        @return     WTSBarStruct的list
        '''
        global bar_cache
        bar_cache = list()
        cnt = self.api.read_dsb_bars(bytes(barFile, encoding="utf8"), cb_read_bar, cb_dthelper_log)
        if cnt == 0:
            return None
        else:
            return bar_cache

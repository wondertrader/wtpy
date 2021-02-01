from ctypes import cdll, CFUNCTYPE, c_char_p, c_void_p
from .PlatformHelper import PlatformHelper as ph
import os

CB_DTHELPER_LOG = CFUNCTYPE(c_void_p,  c_char_p)

def on_log_output(message:str):
    message = bytes.decode(message, "gbk")
    print(message)

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
        self.api.dump_bars(bytes(binFolder, encoding="utf8"), bytes(csvFolder, encoding="utf8"), bytes(strFilter, encoding="utf8"), cb_dthelper_log)

    def dump_ticks(self, binFolder: str, csvFolder: str, strFilter: str=""):
        self.api.dump_ticks(bytes(binFolder, encoding="utf8"), bytes(csvFolder, encoding="utf8"), bytes(strFilter, encoding="utf8"), cb_dthelper_log)

    def trans_csv_bars(self, csvFolder: str, binFolder: str, period: str):
        self.api.trans_csv_bars(bytes(csvFolder, encoding="utf8"), bytes(binFolder, encoding="utf8"), bytes(period, encoding="utf8"), cb_dthelper_log)

from ctypes import cdll, c_char_p, c_int, c_bool, c_double
from .PlatformHelper import PlatformHelper as ph
from wtpy.WtUtilDefs import singleton
import os

@singleton
class WtExecApi:

    # api可以作为公共变量
    api = None
    ver = "Unknown"

    def __init__(self):
        paths = os.path.split(__file__)
        dllname = ph.getModule("WtExecMon")
        a = (paths[:-1] + (dllname,))
        _path = os.path.join(*a)
        self.api = cdll.LoadLibrary(_path)

        self.api.get_version.restype = c_char_p
        self.ver = bytes.decode(self.api.get_version())
        
        self.api.write_log.argtypes = [c_int, c_char_p, c_char_p]
        self.api.config_exec.argtypes = [c_char_p, c_bool]
        self.api.init_exec.argtypes = [c_char_p, c_bool]
        self.api.set_position.argtypes = [c_char_p, c_double]

    def run(self):
        self.api.run_exec()

    def release(self):
        self.api.release_exec()

    def write_log(self, level:int, message:str, catName:str = ""):
        self.api.write_log(level, bytes(message, encoding = "utf8").decode('utf-8').encode('gbk'), bytes(catName, encoding = "utf8"))

    def config(self, cfgfile:str = 'cfgexec.yaml', isFile:bool = True):
        self.api.config_exec(bytes(cfgfile, encoding = "utf8"), isFile)

    def initialize(self, logCfg:str = "logcfgexec.yaml", isFile:bool = True):
        '''
        C接口初始化
        '''
        self.api.init_exec(bytes(logCfg, encoding = "utf8"), isFile)
        self.write_log(102, "WonderTrader independent execution framework initialzied，version: %s" % (self.ver))

    def set_position(self, stdCode:str, target:float):
        self.api.set_position(bytes(stdCode, encoding = "utf8"), target)

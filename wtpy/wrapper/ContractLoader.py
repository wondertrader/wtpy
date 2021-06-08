from .PlatformHelper import PlatformHelper as ph
import os
from ctypes import cdll

from enum import Enum
class LoaderType(Enum):
    '''
    引擎类型
    枚举变量
    '''
    LT_CTP      = 1
    LT_CTPMini  = 2
    LT_CTPOpt   = 3

def getModuleName(lType:LoaderType)->str:
    if lType == LoaderType.LT_CTP:
        filename = "CTPLoader"
    elif lType == LoaderType.LT_CTPMini:
        filename = "CTPMiniLoader"
    elif lType == LoaderType.LT_CTPOpt:
        filename = "CTPOptLoader"
    else:
        raise Exception('Invalid loader type')
        return
    
    paths = os.path.split(__file__)
    exename = ''
    if ph.isWindows(): #windows平台
        if ph.isPythonX64():
            exename = "x64/%s.dll" % (filename)
        else:
            exename = "x86/%s.dll" % (filename)
    else:#Linux平台
        exename = "linux/lib%s.so" % filename
    a = (paths[:-1] + (exename,))
    return os.path.join(*a)


class ContractLoader:

    def __init__(self, lType:LoaderType = LoaderType.LT_CTP):
        print(getModuleName(lType))
        self.api = cdll.LoadLibrary(getModuleName(lType))
        self.api.run.argtypes = [ c_char_p]

    def start(self, cfgfile:str = 'config.ini'):
        self.api.run(bytes(cfgfile, encoding = "utf8"))
from .PlatformHelper import PlatformHelper as ph
import os, json
from ctypes import cdll,c_char_p, c_bool, c_bool

from enum import Enum
class LoaderType(Enum):
    '''
    引擎类型
    枚举变量
    '''
    LT_CTP      = 1
    LT_CTPOpt   = 2

def getModuleName(lType:LoaderType)->str:
    if lType == LoaderType.LT_CTP:
        filename = "CTPLoader"
    elif lType == LoaderType.LT_CTPOpt:
        filename = "CTPOptLoader"
    else:
        raise Exception('Invalid loader type')
        return
    
    paths = os.path.split(__file__)
    exename = ph.getModule(filename)
    a = (paths[:-1] + (exename,))
    return os.path.join(*a)


class ContractLoader:

    def __init__(self, lType:LoaderType = LoaderType.LT_CTP):
        print(getModuleName(lType))
        self.api = cdll.LoadLibrary(getModuleName(lType))
        self.api.run.argtypes = [ c_char_p, c_bool, c_bool]

    def start(self, cfgfile:str = 'config.ini', bAsync:bool = False):
        '''
        启动合约加载器
        @cfgfile    配置文件名
        @bAsync     是否异步，异步则立即返回，默认False
        '''
        self.api.run(bytes(cfgfile, encoding = "utf8"), bAsync, True)

    def start_with_config(self, config:dict, bAsync:bool = False):
        '''
        启动合约加载器
        @cfgfile    配置文件名
        @bAsync     是否异步，异步则立即返回，默认False
        '''
        self.api.run(bytes(json.dumps(config), encoding = "utf8"), bAsync, False)
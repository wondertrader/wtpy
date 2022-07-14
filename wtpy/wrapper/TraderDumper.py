from .PlatformHelper import PlatformHelper as ph
from ctypes import cdll,CFUNCTYPE,c_void_p,c_char_p,c_uint32,c_double,c_bool,c_uint64

import os
import chardet
import yaml
import json

CB_ACCOUNT = CFUNCTYPE(c_void_p, c_char_p, c_uint32, c_char_p, c_double, c_double, c_double, c_double, 
            c_double, c_double, c_double, c_double, c_double, c_bool)
CB_ORDER = CFUNCTYPE(c_void_p, c_char_p, c_char_p, c_char_p, c_uint32, c_char_p, c_uint32, c_uint32, 
            c_double, c_double, c_double, c_double, c_uint32, c_uint32, c_uint64, c_uint32, c_char_p, c_bool)
CB_TRADE = CFUNCTYPE(c_void_p, c_char_p, c_char_p, c_char_p, c_uint32, c_char_p, c_char_p, c_uint32, 
            c_uint32, c_double, c_double, c_double, c_uint32, c_uint32, c_uint64, c_bool)
CB_POSITION = CFUNCTYPE(c_void_p, c_char_p, c_char_p, c_char_p, c_uint32, c_uint32, c_double, c_double, 
            c_double, c_double, c_double, c_uint32, c_bool)

class DumperSink:
    def on_account(self, channelid, curTDate:int, currency, prebalance:float, balance:float, dynbalance:float, 
	        closeprofit:float, dynprofit:float, fee:float, margin:float, deposit:float, withdraw:float, isLast:bool):
        pass

    def on_order(self, channelid, exchg, code, curTDate:int, orderid, direct:int, offset:int, 
            volume:float, leftover:float, traded:float, price:float, ordertype:int, pricetype:int, ordertime:int, state:int, statemsg, isLast:bool):
        pass

    def on_trade(self, channelid, exchg, code, curTDate:int, tradeid, orderid, direct:int, 
            offset:int, volume:float, price:float, amount:float, ordertype:int, tradetype:int, tradetime:int, isLast:bool):
        pass

    def on_position(self, channelid, exchg, code, curTDate:int, direct:int, volume:float, 
            cost:float, margin:float, avgpx:float, dynprofit:float, volscale:int, isLast:bool):
        pass

class TraderDumper:

    def __init__(self, sink:DumperSink, logCfg:str = 'logCfg.yaml'):
        paths = os.path.split(__file__)
        dllname = ph.getModule("TraderDumper")
        a = (paths[:-1] + (dllname,))
        _path = os.path.join(*a)
        self.api = cdll.LoadLibrary(_path)
        self.sink:DumperSink = sink

        self.__config__ = None

        self.api.init(bytes(logCfg, encoding = "utf8"))

        #注册回调函数
        self.cb_account     = CB_ACCOUNT(self.sink.on_account)
        self.cb_order       = CB_ORDER(self.sink.on_order)
        self.cb_trade       = CB_TRADE(self.sink.on_trade)
        self.cb_position    = CB_POSITION(self.sink.on_position)
        self.api.register_callbacks(self.cb_account, self.cb_order, self.cb_trade, self.cb_position)

    def __check_config__(self):
        if self.__config__ is None:
            self.__config__ = dict()

        if "basefiles" not in self.__config__:
            self.__config__["basefiles"] = dict()

        if "traders" not in self.__config__:
            self.__config__["traders"] = list()

    def clear_traders(self):
        self.__config__['traders'] = []

    def add_trader(self, params:dict):
        self.__config__['traders'].append(params)

    def init(self, folder:str,
            cfgfile:str = 'config.yaml',
            commfile:str= None, 
            contractfile:str = None,
            sessionfile:str = None):
        
        if os.path.exists(cfgfile):
            f = open(cfgfile, "rb")
            content = f.read()
            f.close()
            encoding = chardet.detect(content[:500])["encoding"]
            content = content.decode(encoding)

            if cfgfile.lower().endswith(".json"):
                self.__config__ = json.loads(content)
                self.__is_cfg_yaml__ = False
            else:
                self.__config__ = yaml.full_load(content)
                self.__is_cfg_yaml__ = True

        self.__check_config__()

        if contractfile is not None:
            self.__config__["replayer"]["basefiles"]["contract"] = folder + contractfile
        
        if sessionfile is not None:
            self.__config__["replayer"]["basefiles"]["session"] = folder + sessionfile

        if commfile is not None:
            self.__config__["replayer"]["basefiles"]["commodity"] = folder + commfile

    def __commit__(self):
        content = json.dumps(self.__config__, indent=4)
        f = open("config.json", "w")
        f.write(content)
        f.close()
        self.api.config(bytes(content, encoding = "utf8"), False)

    def run(self, bOnce:bool = False):
        self.__commit__()
        self.api.run(bOnce)

    def release(self):
        self.api.release()
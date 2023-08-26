from wtpy.WtDataDefs import WtNpKline, WtNpTicks
from wtpy.WtUtilDefs import singleton
from wtpy.wrapper import WtDtServoApi
import json
import os

@singleton
class WtDtServo:

    # 构造函数, 传入动态库名
    def __init__(self, logcfg:str="logcfg.yaml"):
        self.__config__ = None
        self.__cfg_commited__ = False
        self.local_api = None
        self.logCfg = logcfg

    def __check_config__(self):
        '''
        检查设置项
        主要会补充一些默认设置项
        '''
        if self.local_api is None:
            self.local_api = WtDtServoApi()

        if self.__config__ is None:
            self.__config__ = dict()

        if "basefiles" not in self.__config__:
            self.__config__["basefiles"] = dict()

        if "data" not in self.__config__:
            self.__config__["data"] = {
                "store":{
                    "path":"./storage/"
                }
            }

    def setBasefiles(self, folder:str="./common/", commfile:str="commodities.json", contractfile:str="contracts.json", 
                holidayfile:str="holidays.json", sessionfile:str="sessions.json", hotfile:str="hots.json"):
        '''
        设置基础文件
        @folder 基础文件目录
        @commfile       品种文件, str/list
        @contractfile   合约文件, str/list
        @holidayfile    节假日文件
        @sessionfile    交易时间模板文件
        @hotfile        主力合约配置文件
        '''
        self.__check_config__()

        if type(commfile) == str:
            self.__config__["basefiles"]["commodity"] = os.path.join(folder, commfile)
        elif type(commfile) == list:
            absList = []
            for filename in commfile:
                absList.append(os.path.join(folder, filename))
            self.__config__["basefiles"]["commodity"] = ','.join(absList)

        if type(contractfile) == str:
            self.__config__["basefiles"]["contract"] = os.path.join(folder, contractfile)
        elif type(contractfile) == list:
            absList = []
            for filename in contractfile:
                absList.append(os.path.join(folder, filename))
            self.__config__["basefiles"]["contract"] = ','.join(absList)

        self.__config__["basefiles"]["holiday"] = os.path.join(folder, holidayfile)
        self.__config__["basefiles"]["session"] = os.path.join(folder, sessionfile)
        self.__config__["basefiles"]["hot"] = os.path.join(folder, hotfile)

    def setStorage(self, path:str = "./storage/", adjfactor:str = "adjfactors.json"):
        self.__config__["data"]["store"]["path"] = path
        self.__config__["data"]["store"]["adjfactor"] = adjfactor
    
    def commitConfig(self):            
        if self.__cfg_commited__:
            return

        cfgfile = json.dumps(self.__config__, indent=4, sort_keys=True)
        try:
            self.local_api.initialize(cfgfile, False, self.logCfg)
            self.__cfg_commited__ = True
        except OSError as oe:
            print(oe)

    def clear_cache(self):
        '''
        清除缓存数据
        '''        
        self.local_api.clear_cache()

    def get_bars(self, stdCode:str, period:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtNpKline:
        '''
        获取K线数据
        @stdCode    标准合约代码
        @period     基础K线周期, m1/m5/d
        @fromTime   开始时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM
        @endTime    结束时间, 日线数据格式yyyymmdd, 分钟线数据为格式为yyyymmddHHMM, 为0则读取到最后一条
        '''        
        self.commitConfig()

        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        return self.local_api.get_bars(stdCode=stdCode, period=period, fromTime=fromTime, dataCount=dataCount, endTime=endTime)

    def get_ticks(self, stdCode:str, fromTime:int = None, dataCount:int = None, endTime:int = 0) -> WtNpTicks:
        '''
        获取tick数据
        @stdCode    标准合约代码
        @fromTime   开始时间, 格式为yyyymmddHHMM
        @endTime    结束时间, 格式为yyyymmddHHMM, 为0则读取到最后一条
        '''
        self.commitConfig()

        if (fromTime is None and dataCount is None) or (fromTime is not None and dataCount is not None):
            raise Exception('Only one of fromTime and dataCount must be valid at the same time')

        return self.local_api.get_ticks(stdCode=stdCode, fromTime=fromTime, dataCount=dataCount, endTime=endTime)

    def get_ticks_by_date(self, stdCode:str, iDate:int) -> WtNpTicks:
        '''
        按日期获取tick数据
        @stdCode    标准合约代码
        @iDate      日期, 格式为yyyymmdd
        '''
        self.commitConfig()

        return self.local_api.get_ticks_by_date(stdCode=stdCode, iDate=iDate)

    def get_sbars_by_date(self, stdCode:str, iSec:int, iDate:int) -> WtNpKline:
        '''
        按日期获取秒线数据
        @stdCode    标准合约代码
        @iSec       周期, 单位s
        @iDate      日期, 格式为yyyymmdd
        '''
        self.commitConfig()

        return self.local_api.get_sbars_by_date(stdCode=stdCode, iSec=iSec, iDate=iDate)

    def get_bars_by_date(self, stdCode:str, period:str, iDate:int) -> WtNpKline:
        '''
        按日期获取K线数据
        @stdCode    标准合约代码
        @period     周期，只支持分钟线
        @iDate      日期, 格式为yyyymmdd
        '''
        self.commitConfig()

        return self.local_api.get_bars_by_date(stdCode=stdCode, period=period, iDate=iDate)